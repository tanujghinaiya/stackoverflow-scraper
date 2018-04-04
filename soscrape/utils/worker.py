import multiprocessing

from soscrape.utils.request_handler import RequestsHandler


class Worker(multiprocessing.Process):
    def __init__(self, task_queue, result_queue, **kwargs):
        super(Worker, self).__init__()
        self.task_queue = task_queue
        self.result_queue = result_queue
        self.kwargs = kwargs
        self.task_kwargs = {}

    def run(self):
        if 'requests_handler' in self.kwargs:
            if 'requests_handler' not in self.task_kwargs and self.kwargs['requests_handler']:
                self.task_kwargs['requests_handler'] = RequestsHandler()
                print('Initialized request handler for {}'.format(self.name))

        try:
            for task in iter(self.task_queue.get, None):
                result = task(**self.task_kwargs)

                self.result_queue.put(result)
        except KeyboardInterrupt:
            pass
        except Exception as e:
            raise e
        finally:
            return
