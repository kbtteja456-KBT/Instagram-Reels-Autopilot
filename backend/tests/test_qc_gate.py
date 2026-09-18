"""Unit tests for the strict Quality Control (QC >= 90) evaluation."""

import asyncio
from unittest.mock import patch
from backend.app.agents.qc import QCAgent


def test_qc_gate_passes_for_compliant_reel():
    async def _run():
        agent = QCAgent()

        mock_probe = {
            "width": 1080,
            "height": 1920,
            "fps": 30.0,
            "duration": 42.0,
            "has_audio": True
        }

        with patch("os.path.exists", return_value=True), \
             patch("backend.app.agents.qc.probe_video_stream", return_value=mock_probe):
            
            report = await agent.audit_video("/fake/reel.mp4")
            assert report.passed is True
            assert report.score >= 90.0

    asyncio.run(_run())


def test_qc_gate_fails_for_wrong_resolution():
    async def _run():
        agent = QCAgent()

        # Landscape 1920x1080 instead of vertical 1080x1920
        mock_probe = {
            "width": 1920,
            "height": 1080,
            "fps": 30.0,
            "duration": 42.0,
            "has_audio": True
        }

        with patch("os.path.exists", return_value=True), \
             patch("backend.app.agents.qc.probe_video_stream", return_value=mock_probe):
            
            report = await agent.audit_video("/fake/reel.mp4")
            assert report.score < 90.0
            assert report.passed is False
            assert "expected 1080x1920" in report.remediation_notes

    asyncio.run(_run())
