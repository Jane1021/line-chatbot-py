import argparse
import json
import os
from punctuator import Punctuator
from dotenv import load_dotenv

try:
    from utils import PathHelper, get_logger
except Exception as e:
    print(e)
    raise ("Please run this script from the root directory of the project")

# load env variables
dotenv_path = PathHelper.root_dir / ".env"
load_dotenv(dotenv_path=dotenv_path)

# logger
logger = get_logger(__name__)

# init Punctuator model
logger.info("Init Punctuator model")
punctuator = Punctuator(PathHelper.punctuator_model_path)


# process functions
def preprocess_transcript(transcript):
    """
    Add punctuation to transcript and merge into one document
    """
    # Add punctuation to transcript
    transcript_with_punctuation = punctuator.punctuate(transcript)

    return transcript_with_punctuation


def main(args):
    # Select files
    entities = [i for i in os.listdir(PathHelper.entities_dir) if i.endswith(".json")]

    logger.info(f"# files: {len(entities)}")

    # Text to text
    m_transcripts_processed = 0
    for jf in entities:
        fname = jf.split(".")[0]
        try:
            with open(PathHelper.entities_dir / jf, "r") as f:
                ent_i = json.load(f)

            # If file exists, then skip
            if (PathHelper.text_dir / f"{fname}.txt").exists():
                logger.info(f"File exists: {fname}")
                continue

            # If having transcript from entities, then save text
            if ent_i.get("transcript"):
                transcript_text = "\n".join([t["text"] for t in ent_i["transcript"]])

                # Preprocess transcript
                transcript_with_punctuation = preprocess_transcript(transcript_text)

                # Save transcript with encoding
                with open(PathHelper.text_dir / f"{fname}.txt", "w", encoding="utf-8") as f:
                    f.write(transcript_with_punctuation)

                m_transcripts_processed += 1

        except Exception as e:
            logger.error(e)
            continue

    # Logger
    logger.info(f"Extract transcript from {m_transcripts_processed} files")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    args = parser.parse_args()
    main(args)
