import sys

def check_env():
    print("=== [1] ENVIRONMENT VALIDATION ===")
    print(f"Python version: {sys.version}")
    assert sys.version_info >= (3, 8), "Python 3.8+ required"
    
    packages = ["numpy", "scipy", "pandas", "statsmodels", "pytest"]
    for pkg in packages:
        try:
            mod = __import__(pkg)
            version = getattr(mod, "__version__", "unknown")
            print(f"  {pkg:15s}: {version} (OK)")
        except ImportError:
            print(f"  {pkg:15s}: NOT INSTALLED")
            sys.exit(1)
    print("Environment validation: ALL CHECKS PASSED.\n")

if __name__ == '__main__':
    check_env()
