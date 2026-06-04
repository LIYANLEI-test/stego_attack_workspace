from __future__ import annotations

import csv
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

import numpy as np
from PIL import Image


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

import attack_common
import render_paper_tables as render
import select_quality_budget_attacks as selector
import select_target_psnr_attacks as target_selector
import summarize_attack_deltas as deltas
import summarize_selected_attack_runs as summary
import audit_selected_attack_results as audit
from selected_attack_matrix import SELECTED_ATTACKS


def write_rows(path: Path, rows: list[dict[str, object]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)


class SelectedSummaryTests(unittest.TestCase):
    def test_formal_summary_excludes_calibration_and_scores_saved_reveal_failure(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            spec = SELECTED_ATTACKS[0]
            out = root / f"{spec.method}_{spec.name_part}_100"
            stego = out / "stego.png"
            attacked = out / "attacked.png"
            stego.parent.mkdir(parents=True)
            stego.touch()
            attacked.touch()
            write_rows(
                out / "identity_results.csv",
                [
                    {"sample_index": 0, "bit_accuracy": 0.99, "exact_match": "False", "runtime_s": 1.0},
                    {"sample_index": 10, "bit_accuracy": 0.8, "exact_match": "False", "runtime_s": 1.0},
                ],
            )
            write_rows(
                out / "identity_failures.csv",
                [{"sample_index": 11, "stego_path": stego, "attacked_path": attacked, "runtime_s": 1.0}],
            )
            with patch.object(summary, "quality_values", return_value=([40.0, 40.0], [1.0, 1.0], [])):
                row = summary.summarize_one(root, spec, "cpu", False, 2, False)
            self.assertEqual(row["rows"], 1)
            self.assertEqual(row["failures"], 1)
            self.assertEqual(row["unscorable_failures"], 0)
            self.assertEqual(row["recovery_mean"], 0.4)
            self.assertTrue(row["complete"])

    def test_unscorable_failure_does_not_complete_formal_row(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            spec = SELECTED_ATTACKS[0]
            out = root / f"{spec.method}_{spec.name_part}_100"
            write_rows(
                out / "identity_results.csv",
                [{"sample_index": 10, "recovery_psnr": 20.0, "exact_match": "False", "runtime_s": 1.0}],
            )
            write_rows(out / "identity_failures.csv", [{"sample_index": 11, "runtime_s": 1.0}])
            with patch.object(summary, "quality_values", return_value=([40.0], [1.0], [])):
                row = summary.summarize_one(root, spec, "cpu", False, 2, False)
            self.assertEqual(row["total"], 1)
            self.assertEqual(row["unscorable_failures"], 1)
            self.assertFalse(row["complete"])


class QualityAndTableTests(unittest.TestCase):
    def test_soft_blur_factors_create_milder_non_identity_attacks(self) -> None:
        array = np.zeros((7, 7, 3), dtype=np.uint8)
        array[:, :3] = 255
        array[3, 3] = 255
        image = Image.fromarray(array, "RGB")

        median_soft = np.asarray(attack_common.median_blur_pil(image, 0.5))
        median_full = np.asarray(attack_common.median_blur_pil(image, 3))
        self.assertGreater(np.abs(median_soft.astype(int) - array.astype(int)).sum(), 0)
        self.assertLess(
            np.abs(median_soft.astype(int) - array.astype(int)).sum(),
            np.abs(median_full.astype(int) - array.astype(int)).sum(),
        )

        gaussian_soft = np.asarray(attack_common.gaussian_blur_pil(image, 0.5))
        self.assertGreater(np.abs(gaussian_soft.astype(int) - array.astype(int)).sum(), 0)

    def test_scad_lite_calibrates_to_target_psnr(self) -> None:
        yy, xx = np.indices((32, 32), dtype=np.uint8)
        array = np.stack(
            [
                (xx * 7 + yy * 3) % 255,
                (xx * 5 + 31) % 255,
                (yy * 9 + 17) % 255,
            ],
            axis=2,
        ).astype(np.uint8)
        image = Image.fromarray(array, "RGB")
        attacked = np.asarray(attack_common.scad_lite_pil(image, 30.0), dtype=np.uint8)
        mse = np.mean((array.astype(np.float32) - attacked.astype(np.float32)) ** 2)
        psnr = 20.0 * np.log10(255.0 / np.sqrt(mse))
        self.assertGreaterEqual(psnr, 29.5)
        self.assertLessEqual(psnr, 30.5)
        self.assertEqual(attack_common.attack_suffix("scad", attack_factor=30), "scad_p30")

    def test_selector_requires_complete_psnr_and_lpips_coverage(self) -> None:
        good = {
            "scored_total": 2,
            "unscorable_failures": 0,
            "quality_psnr_n": 2,
            "quality_lpips_n": 2,
            "quality_psnr_mean": 31.0,
            "quality_lpips_mean": 0.09,
        }
        self.assertTrue(selector.is_within_budget(good, 30.0, 0.10))
        self.assertFalse(selector.is_within_budget({**good, "quality_lpips_n": 1}, 30.0, 0.10))
        self.assertFalse(selector.is_within_budget({**good, "quality_lpips_mean": ""}, 30.0, 0.10))

    def test_target_psnr_selector_prefers_quality_alignment_then_strength(self) -> None:
        base = {
            "method": "gsd_cifar10",
            "attack": "jpeg",
            "rows": "10",
            "failures": "0",
            "unscorable_failures": "0",
            "scored_total": "10",
            "quality_psnr_n": "10",
            "quality_lpips_n": "10",
            "quality_lpips_mean": "0.05",
            "metric": "bit_accuracy",
            "exact": "0",
        }
        rows = [
            {**base, "factor": "90", "quality_psnr_mean": "29.9", "metric_mean": "0.9"},
            {**base, "factor": "70", "quality_psnr_mean": "30.5", "metric_mean": "0.1"},
        ]
        selected = target_selector.select_rows(rows, 30.0, 1.0)
        self.assertEqual(selected[0]["factor"], "90")

        rows = [
            {**base, "factor": "80", "quality_psnr_mean": "29.8", "metric_mean": "0.8"},
            {**base, "factor": "70", "quality_psnr_mean": "30.2", "metric_mean": "0.7"},
        ]
        selected = target_selector.select_rows(rows, 30.0, 1.0)
        self.assertEqual(selected[0]["factor"], "70")

    def test_target_psnr_bit_summary_reports_ber_and_failure_rate(self) -> None:
        selected = [
            {
                "method": "gsd_cifar10",
                "attack": "jpeg",
                "factor": "70",
                "metric": "bit_accuracy",
                "metric_mean": "0.6",
                "quality_psnr_mean": "30.0",
                "quality_lpips_mean": "0.05",
                "psnr_gap_abs": "0.0",
                "bit_destruction_rate": 0.4,
                "reveal_failure_rate": 0.0,
                "exact_destruction_rate": 1.0,
            },
            {
                "method": "pulsar",
                "attack": "jpeg",
                "factor": "50",
                "metric": "bit_accuracy",
                "metric_mean": "0.0",
                "quality_psnr_mean": "38.0",
                "quality_lpips_mean": "0.03",
                "psnr_gap_abs": "8.0",
                "bit_destruction_rate": 1.0,
                "reveal_failure_rate": 1.0,
                "exact_destruction_rate": 1.0,
            },
        ]
        summary_rows = target_selector.summarize_bit_attacks(selected)
        self.assertEqual(summary_rows[0]["attack"], "jpeg")
        self.assertAlmostEqual(summary_rows[0]["mean_bit_destruction_rate"], 0.7)
        self.assertAlmostEqual(summary_rows[0]["mean_reveal_failure_rate"], 0.5)

    def test_target_psnr_selector_can_restrict_to_bit_payload_methods(self) -> None:
        base = {
            "attack": "jpeg",
            "rows": "10",
            "failures": "0",
            "unscorable_failures": "0",
            "scored_total": "10",
            "quality_psnr_n": "10",
            "quality_lpips_n": "10",
            "quality_psnr_mean": "30.0",
            "quality_lpips_mean": "0.05",
            "metric_mean": "0.6",
            "exact": "0",
        }
        rows = [
            {**base, "method": "cross", "factor": "50", "metric": "recovery_psnr"},
            {**base, "method": "gsd_cifar10", "factor": "70", "metric": "bit_accuracy"},
        ]
        selected = target_selector.select_rows(
            rows,
            30.0,
            1.0,
            include_methods=target_selector.BIT_PAYLOAD_METHODS,
        )
        self.assertEqual([row["method"] for row in selected], ["gsd_cifar10"])

    def test_table_separates_appendix_and_shows_conditional_delta(self) -> None:
        base = {
            "attack": "jpeg",
            "factor": "70",
            "label": "jpeg_q70",
            "metric": "bit_accuracy",
            "total": "40",
            "target": "40",
            "recovery_mean": "0.5",
            "delta_delta_mean": "0.2",
            "delta_delta_on_identity_success_mean": "0.3",
            "quality_psnr_mean": "31.0",
            "quality_psnr_n": "40",
            "quality_lpips_mean": "0.05",
            "quality_lpips_n": "40",
            "failure_rate": "0",
        }
        text = render.render_markdown(
            [
                {**base, "method": "gsd_cifar10", "provenance": "native_official"},
                {**base, "method": "mddm_128_pilot", "provenance": "native_third_party"},
            ]
        )
        main, appendix = text.split("## Appendix Pilot Table")
        self.assertIn("gsd_cifar10", main)
        self.assertNotIn("mddm_128_pilot", main)
        self.assertIn("mddm_128_pilot", appendix)
        self.assertIn("Delta (ID-ok)", text)

    def test_render_excludes_image_payload_methods_from_current_main_table(self) -> None:
        base = {
            "attack": "jpeg",
            "factor": "70",
            "label": "jpeg_q70",
            "metric": "bit_accuracy",
            "total": "40",
            "target": "40",
            "recovery_mean": "0.5",
            "quality_psnr_mean": "31.0",
            "quality_lpips_mean": "0.05",
            "failure_rate": "0",
        }
        text = render.render_markdown(
            [
                {**base, "method": "cross", "provenance": "native_official", "metric": "recovery_psnr"},
                {**base, "method": "gsd_cifar10", "provenance": "native_official"},
            ]
        )
        main = text.split("## Appendix Pilot Table")[0] if "## Appendix Pilot Table" in text else text
        self.assertNotIn("cross", main)
        self.assertIn("gsd_cifar10", main)

    def test_render_does_not_hide_incomplete_row_in_final_mode(self) -> None:
        rows = render.merged_rows(
            [{"method": "pulsar", "attack": "jpeg", "factor": "95", "complete": "False"}],
            [],
            include_incomplete=False,
        )
        self.assertEqual(len(rows), 1)

    def test_final_audit_does_not_hide_incomplete_unscorable_row(self) -> None:
        summary_rows = [
            {
                "method": "pulsar",
                "attack": "jpeg",
                "factor": "95",
                "provenance": "native_official",
                "complete": "False",
                "total": "0",
                "unscorable_failures": "1",
            }
        ]
        rows = audit.audit_rows(summary_rows, [], include_incomplete=False)
        self.assertEqual(len(rows), 1)
        self.assertEqual(rows[0]["budget_status"], "fail")
        self.assertIn("unscorable_failures=1", rows[0]["paper_caveats"])


class DeltaFailureTests(unittest.TestCase):
    def test_attack_failure_requires_saved_pair_for_zero_score(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            directory = Path(temp)
            stego = directory / "stego.png"
            attacked = directory / "attacked.png"
            stego.touch()
            attacked.touch()
            write_rows(
                directory / "identity_failures.csv",
                [
                    {"sample_index": 10, "stego_path": stego, "attacked_path": attacked},
                    {"sample_index": 11, "stego_path": stego, "attacked_path": ""},
                ],
            )
            values, _, scored, unscored, _ = deltas.load_metric_map(directory, "pulsar", False, True)
            self.assertEqual(values, {10: 0.0})
            self.assertEqual(scored, 1)
            self.assertEqual(unscored, 1)

    def test_old_gsd_failure_row_can_recover_saved_attack_pair_from_run_layout(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            directory = Path(temp)
            images = directory / "images"
            images.mkdir()
            (images / "stego_000010.png").touch()
            (images / "stego_000010_resize_1_25.png").touch()
            write_rows(directory / "identity_failures.csv", [{"sample_index": 10}])
            values, _, scored, unscored, _ = deltas.load_metric_map(directory, "gsd_cifar10", False, True)
            self.assertEqual(values, {10: 0.0})
            self.assertEqual(scored, 1)
            self.assertEqual(unscored, 0)


if __name__ == "__main__":
    unittest.main()
