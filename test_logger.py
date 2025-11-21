"""
Test script to demonstrate logger functionality
"""
import logging
from utils.logger import setup_logger, app_logger
from core.triangle import TriangleManager
from core.cone_calculator import ConeCalculator
from utils.config import Config


def test_logger():
    """Test the logger functionality"""
    print("Testing logger functionality...")
    
    # Test the default logger
    app_logger.info("This is an info message from the default logger")
    app_logger.debug("This is a debug message from the default logger")
    app_logger.warning("This is a warning message from the default logger")
    
    # Test creating a custom logger
    custom_logger = setup_logger('custom_logger', logging.DEBUG)
    custom_logger.info("This is an info message from a custom logger")
    custom_logger.debug("This is a debug message from a custom logger")
    
    # Test logging in components
    config = Config()
    config.set_pixel_size(0.005)
    
    triangle_manager = TriangleManager()
    triangle_manager.add_vertex(0, 0)
    triangle_manager.add_vertex(100, 0)
    triangle_manager.add_vertex(50, 100)
    
    if triangle_manager.is_complete():
        cone_params = ConeCalculator.get_cone_parameters(
            triangle_manager.vertices,
            config.pixel_size_m
        )
        print(f"Cone volume: {cone_params['volume']}")


if __name__ == "__main__":
    test_logger()