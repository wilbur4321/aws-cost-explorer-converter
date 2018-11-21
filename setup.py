from setuptools import setup

setup(name='aws_cost_explorer_converter',
      version='0.1',
      description='Code and tool to call aws costexplorer and convert to Pandas Dataframe or CSV',
      url='http://github.com/wilbur4321/aws-cost-explorer-converter',
      author='Randy Chapman',
      author_email='randy.chapman@spglobal.com',
      license='MIT',
      packages=['aws_cost_explorer_converter'],
      entry_points = {
            'console_scripts': ['aws-cost-explorer-converter=aws_cost_explorer_converter.command_line:main'],
            },
      zip_safe=False)
