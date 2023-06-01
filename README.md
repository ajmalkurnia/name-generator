# Name Generator

A simple name generator with simple character level markov chain implemented from scratch with numpy. Site at: [name.ajkurnia.com](name.ajkurnia.com)

## Usage

### 1. Build Model

- Prepare your dataset, a simple .txt file listing each name/string in each line
- Use the `run.py` to train a markov model with your dataset, see `run.py --help` for more info.
- To generate some samples use command `run.py --load-model PATH/TO/MODEL --generate x`

### 2. Service

- There is a flask script you can use to serve the model on a simple web interface
- The model can be loaded via regular file read or via GCS, support for S3 may come later.
- You can limit the api access with flask limiter by setting the `LIMITER_STORAGE_URI` see `flask_limiter` for more details
