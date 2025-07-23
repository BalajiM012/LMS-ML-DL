#!/usr/bin/env python3
"""
TensorFlow Installation Helper
This script attempts to install TensorFlow and provides fallback solutions
"""

import subprocess
import sys
import platform
import importlib.util

def check_python_version():
    """Check if Python version is compatible with TensorFlow"""
    version = sys.version_info
    print(f"Python version: {version.major}.{version.minor}.{version.micro}")
    
    # TensorFlow 2.15.0 requires Python 3.8-3.11
    if version.major == 3 and 8 <= version.minor <= 11:
        return True
    else:
        print("Warning: Python version may not be compatible with TensorFlow 2.15.0")
        return False

def check_platform():
    """Check platform compatibility"""
    system = platform.system()
    machine = platform.machine()
    print(f"Platform: {system} {machine}")
    
    # TensorFlow supports these platforms
    supported = {
        'Windows': ['AMD64', 'x86_64'],
        'Linux': ['x86_64', 'aarch64'],
        'Darwin': ['x86_64', 'arm64']
    }
    
    if system in supported and machine in supported[system]:
        return True
    else:
        print(f"Warning: {system} {machine} may not be fully supported")
        return False

def install_tensorflow():
    """Attempt to install TensorFlow with platform-specific packages"""
    packages = [
        "tensorflow==2.15.0",
        "tensorflow-cpu==2.15.0",
        "tensorflow-macos==2.15.0",  # For Apple Silicon
    ]
    
    for package in packages:
        try:
            print(f"Attempting to install {package}...")
            subprocess.check_call([sys.executable, "-m", "pip", "install", package])
            
            # Verify installation
            spec = importlib.util.find_spec("tensorflow")
            if spec is not None:
                import tensorflow as tf
                print(f"✅ Successfully installed {package}")
                print(f"TensorFlow version: {tf.__version__}")
                return True
        except subprocess.CalledProcessError as e:
            print(f"❌ Failed to install {package}: {e}")
            continue
        except ImportError:
            print(f"❌ Package {package} installed but not importable")
            continue
    
    return False

def setup_mock_tensorflow():
    """Setup mock TensorFlow when installation fails"""
    print("Setting up mock TensorFlow implementation...")
    
    # Create __init__.py files if needed
    import os
    tensorflow_dir = os.path.join(os.path.dirname(__file__), 'src', 'tensorflow')
    os.makedirs(tensorflow_dir, exist_ok=True)
    
    # Create mock __init__.py
    init_content = '''
"""
Mock TensorFlow module
Provides compatibility when TensorFlow is not available
"""
from src.tensorflow_compat import tf, HAS_TENSORFLOW

__all__ = ['tf', 'HAS_TENSORFLOW']
'''
    
    with open(os.path.join(tensorflow_dir, '__init__.py'), 'w') as f:
        f.write(init_content)
    
    print("✅ Mock TensorFlow setup complete")

def main():
    """Main installation process"""
    print("🚀 TensorFlow Installation Helper")
    print("=" * 50)
    
    # Check compatibility
    python_ok = check_python_version()
    platform_ok = check_platform()
    
    if python_ok and platform_ok:
        print("\n📦 Attempting TensorFlow installation...")
        if install_tensorflow():
            print("\n✅ TensorFlow installation successful!")
            return
    
    print("\n⚠️  TensorFlow installation failed or not compatible")
    print("🔧 Setting up mock TensorFlow implementation...")
    setup_mock_tensorflow()
    
    print("\n📋 Next steps:")
    print("1. Use the mock implementation (already configured)")
    print("2. For manual installation, try:")
    print("   pip install tensorflow==2.15.0 --no-cache-dir")
    print("   pip install tensorflow-cpu==2.15.0 --no-cache-dir")
    print("3. Check Python version compatibility (3.8-3.11)")
    print("4. Verify platform support (Windows/Linux/Mac x86_64)")

if __name__ == "__main__":
    main()
