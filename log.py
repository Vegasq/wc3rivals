import logging

LOG = logging.getLogger("classicbnet")
LOG.setLevel(logging.INFO)

ch = logging.StreamHandler()
formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
ch.setFormatter(formatter)

LOG.addHandler(ch)

