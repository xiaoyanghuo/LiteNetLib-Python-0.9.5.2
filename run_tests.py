#!/usr/bin/env python
"""
Test Runner for LiteNetLib-Python / LiteNetLib-Python 测试运行器

Quick script to run all tests with appropriate options.
"""

import sys
import subprocess


def run_tests(args=None):
    """Run pytest with appropriate options / 运行 pytest 及适当选项"""
    cmd = [sys.executable, "-m", "pytest", "tests/", "-v"]

    if args:
        cmd.extend(args)

    print(f"Running: {' '.join(cmd)}\n")
    result = subprocess.run(cmd)
    return result.returncode


def main():
    """Main entry point / 主入口"""
    import argparse

    parser = argparse.ArgumentParser(description="Run LiteNetLib-Python tests")
    parser.add_argument("--integration", action="store_true",
                       help="Run integration tests (requires network)")
    parser.add_argument("--unit", action="store_true",
                       help="Run only unit tests (no network)")
    parser.add_argument("--coverage", action="store_true",
                       help="Generate coverage report")
    parser.add_argument("--file", type=str,
                       help="Run specific test file")
    parser.add_argument("--quick", action="store_true",
                       help="Quick test run (skip integration and slow tests)")

    args = parser.parse_args()
    pytest_args = []

    if args.integration:
        pytest_args.extend(["-v", "-m", "integration"])
    elif args.unit:
        pytest_args.extend(["-v", "-m", "not integration"])
    elif args.quick:
        pytest_args.extend(["-v", "-m", "not integration"])
    elif args.coverage:
        pytest_args.extend(["--cov=litenetlib", "--cov-report=html", "--cov-report=term"])
    elif args.file:
        pytest_args.extend([args.file, "-v"])
    else:
        # Default: run all tests
        pytest_args.extend(["-v", "-x"])  # -x stops on first failure

    return run_tests(pytest_args)


if __name__ == "__main__":
    sys.exit(main())
