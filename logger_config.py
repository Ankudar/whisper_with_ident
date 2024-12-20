# pylint: disable-msg=line-too-long
# pylint: disable-msg=broad-exception-caught
# pylint: disable-msg=missing-function-docstring
# pylint: disable-msg=invalid-name

import logging

class IgnoreEstimateDurationFilter(logging.Filter):
    def filter(self, record):
        return 'Estimating duration from bitrate' not in record.getMessage()

log_file = ".\\errors.log"
logging.basicConfig(filename=log_file, encoding="utf-8", filemode='w', format='%(name)s - %(levelname)s - %(asctime)s - %(message)s - %(pathname)s - %(lineno)d - %(funcName)s \n')

# Add the filter to the root logger
root_logger = logging.getLogger()
root_logger.addFilter(IgnoreEstimateDurationFilter())
