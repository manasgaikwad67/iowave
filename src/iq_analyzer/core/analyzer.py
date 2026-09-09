"""High-level analyzer interface."""

from pathlib import Path
from typing import Optional, Dict, Any
from ..models import AnalysisResult
from ..core.pipeline import run_analysis_pipeline, PipelineConfig, create_pipeline_config_from_settings
from ..utils import get_logger

logger = get_logger(__name__)


class IQSignalAnalyzer:
    """
    High-level interface for IQ signal analysis.

    This class provides a simple interface for analyzing signal files
    with customizable configuration.
    """

    def __init__(self, config: Optional[PipelineConfig] = None):
        """
        Initialize analyzer.

        Args:
            config: Pipeline configuration. If None, uses defaults from settings.
        """
        self.config = config or create_pipeline_config_from_settings()

    def analyze_file(
        self,
        file_path: Path,
        sample_rate: Optional[float] = None,
        dtype: Optional[str] = None,
        endianness: Optional[str] = None,
        iq_layout: Optional[str] = None,
        force_iq: bool = False,
    ) -> AnalysisResult:
        """
        Analyze a signal file.

        Args:
            file_path: Path to signal file
            sample_rate: Sample rate (required for raw IQ)
            dtype: Data type (for raw IQ)
            endianness: Endianness (for raw IQ)
            iq_layout: IQ layout (for raw IQ)
            force_iq: Force stereo WAV as IQ

        Returns:
            AnalysisResult
        """
        return run_analysis_pipeline(
            file_path=file_path,
            config=self.config,
            sample_rate=sample_rate,
            dtype=dtype,
            endianness=endianness,
            iq_layout=iq_layout,
            force_iq=force_iq,
        )

    def analyze_iq_data(
        self,
        iq_data,
        sample_rate: float,
    ) -> AnalysisResult:
        """
        Analyze raw IQ data array.

        Args:
            iq_data: Complex IQ signal array
            sample_rate: Sample rate in Hz

        Returns:
            AnalysisResult
        """
        # This would need a modified pipeline that skips file loading
        # For now, raise not implemented
        raise NotImplementedError("Direct IQ data analysis not yet implemented. Use analyze_file.")

    def update_config(self, config: PipelineConfig) -> None:
        """Update analyzer configuration."""
        self.config = config


def analyze_file(
    file_path: Path,
    sample_rate: Optional[float] = None,
    dtype: Optional[str] = None,
    endianness: Optional[str] = None,
    iq_layout: Optional[str] = None,
    force_iq: bool = False,
    config: Optional[PipelineConfig] = None,
) -> AnalysisResult:
    """
    Convenience function for analyzing a single file.

    Args:
        file_path: Path to signal file
        sample_rate: Sample rate (required for raw IQ)
        dtype: Data type (for raw IQ)
        endianness: Endianness (for raw IQ)
        iq_layout: IQ layout (for raw IQ)
        force_iq: Force stereo WAV as IQ
        config: Pipeline configuration

    Returns:
        AnalysisResult
    """
    analyzer = IQSignalAnalyzer(config)
    return analyzer.analyze_file(
        file_path=file_path,
        sample_rate=sample_rate,
        dtype=dtype,
        endianness=endianness,
        iq_layout=iq_layout,
        force_iq=force_iq,
    )