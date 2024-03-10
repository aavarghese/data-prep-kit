# Data Processing Library
This provides a python framework for developing _transforms_ 
on data stored in files - currently parquet files are supported -
and running them in a [ray](https://ray.com) cluster.
Data files may be stored in the local file system, COS/S3 or Lakehouse.
For more details see the [documentation](doc).

## Development

### Requirements
1. python 3.9 or later
2. git command line tools
3. [pre-commit](https://pre-commit.com/)
4. twine (pip install twine)
    * but on Mac you may have to include a dir in your PATH, such as `export PATH=$PATH:/Library/Frameworks/Python.framework/Versions/3.10/bin`

### Git
Simple clone the repo and set up the pre-commit hooks.
```shell
git clone git@github.ibm.com:ai-models-data/fm-data-engineering.git
cd fm-data-engineering
pre-commit install
```
If you don't have pre-commit, you can install from [here](https://pre-commit.com/)

### Virtual Environment
The project uses pyproject.toml and a Makefile for operations.
To do development you should establish the virtual environment
```shell
make venv
```
and then either activate
```shell
source venv/bin/activate
```
or set up your IDE to use the venv directory when developing in this project


## Library Artifact Build and Publish
To build and publish the library to artifactory
```shell
make build
make publish
```
To up the version number, edit the Makefile to change VERSION and rerun
the above.  This will require committing both the Makefile and the 
autotmatically updated pyproject.toml file.

## Development (OLD?)

Start by installing `setup-tools`

```shell
pip3 install -U setuptools
```

Now install our library locally. From the directory `path/to/kuberay/clients/python_apiserver_client` execute

```shell
pip3 install -e .
```

## Testing
