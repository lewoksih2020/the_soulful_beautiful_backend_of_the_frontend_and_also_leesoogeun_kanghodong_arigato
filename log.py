import logging
from colorlog import ColoredFormatter


def setup_logger():
    """Return a logger with a default ColoredFormatter."""
    formatter = ColoredFormatter(
        (
            '%(log_color)s%(levelname)-5s%(reset)s '
            '%(yellow)s[%(asctime)s]%(reset)s'
            '%(green)s %(name)s %(purple)s %(filename)s %(purple)s %(funcName)s %(purple)s:%(lineno)d%(reset)s '
            '%(bold_blue)s%(message)s%(reset)s'
        ),
        datefmt='%y-%m-%d %H;%M:%S',
        log_colors={
            'DEBUG': 'blue',
            'INFO': 'yellow',
            'WARNING': 'red',
            'ERROR': 'blue,bg_bold_red',
            'CRITICAL': 'red,bg_white',
        }
    )

    logger = logging.getLogger('shen-yue-is-beautiful')
    handler = logging.StreamHandler()
    handler.setFormatter(formatter)
    logger.addHandler(handler)
    logger.setLevel(logging.DEBUG)

    return logger


def main():
    """Create and use a logger."""
    logger = setup_logger()

    logger.debug('a debug message')
    logger.info('an info message')
    logger.warning('a warning message')
    logger.error('an error message')
    logger.critical('a critical message')


if __name__ == '__main__':
    main()