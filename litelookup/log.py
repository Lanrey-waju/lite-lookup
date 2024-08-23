import logging

logger = logging.getLogger("lite_lookup")
logger.setLevel(logging.DEBUG)

ch = logging.StreamHandler()
ch.setLevel(logging.ERROR)
ch.setLevel(logging.INFO)

formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
ch.setFormatter(formatter)

fh = logging.FileHandler("trace.log")
fh.setLevel(logging.DEBUG)
fh.setLevel(logging.ERROR)
fh.setFormatter(formatter)

logger.addHandler(ch)
logger.addHandler(fh)
