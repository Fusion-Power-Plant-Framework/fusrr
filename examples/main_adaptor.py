"""Executes adaptor.py"""
import argparse

from renderingpipeline.adaptor import OutputParams


def main():
    """Pass in file and call to generate generic output"""
    argparser = argparse.ArgumentParser()
    argparser.add_argument("-fn", "--file_name", help="input file")
    args = argparser.parse_args()
    file_name = str(args.file_name)
    generic_output = OutputParams.from_file(file_name)
    print("generic_output=", generic_output)
    return generic_output


if __name__ == "__main__":
    generic_output = main()
