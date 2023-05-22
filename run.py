import argparse

from model.markov import MarkovGenerator
from utils.common import measure_time


def main(args):
  if not args.corpus and not args.load_model:
    raise ValueError("Use --corpus or --load-model")
  elif args.load_model:
    model = MarkovGenerator.load(args.load_model)
  elif args.corpus:
    with open(args.corpus, "r") as f:
      if args.lower:
        data = f.read().strip().lower().split("\n")
      else:
        data = f.read().strip().split("\n")
    model = MarkovGenerator(args.state)
    measure_time(model.fit, data, args.smooth)

  for i in range(args.generate):
    print(measure_time(model.generate))

  if args.save_model:
    model.save(args.save_model, args.save_lite)


if __name__ == "__main__":
  parser = argparse.ArgumentParser(
    description="Character level markov generator demo"
  )
  parser.add_argument(
    "state", metavar="N", type=int, default=2, help="Number of markov state"
  )
  parser.add_argument(
    "--corpus", type=str, help="Corpus File" 
  )
  parser.add_argument(
    "--smooth", action="store_true", help="Perform laplace smoothing"
  )
  parser.add_argument(
    "--lower", action="store_true", help="Perform lower casing"
  )
  parser.add_argument(
    "--save-model", type=str, help="Path to save trained model"
  )
  parser.add_argument(
    "--save-lite", action="store_true", help="Save the lite model instead of the full one"
  )
  parser.add_argument(
    "--load-model", type=str, help="Path to existing pretrained model"
  )
  parser.add_argument(
    "--generate", type=int, help="Generate Samples", default=1
  )
  args = parser.parse_args()
  main(args)
