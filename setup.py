from setuptools import setup


install_requires = [
    'numpy',
    'pandas',
    'pyyaml',
]

setup(name='cricsheet',
      version='0.1',
      description='Dealing with CricSheet data',
      url='http://github.com/kochhar/cricsheet',
      author='Shailesh Kochhar',
      author_email='shailesh.kochhar@gmail.com',
      license='MIT',
      packages=['cric'],
      install_requires=install_requires,
      scripts=[
        'bin/load_cric_data.py'
      ],
      zip_safe=False)
