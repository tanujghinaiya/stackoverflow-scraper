import multiprocessing
import os

from soscrape.utils.progress_bar import ProgressBar
from soscrape.utils.worker import Worker


class TasksHandler:
    @staticmethod
    def map(tasks, n_tasks=None, n_workers=None, ipython_notebook=False, **kwargs):
        results = []

        try:
            tasks_queue = multiprocessing.Queue()
            results_queue = multiprocessing.Queue()
            pbar = ProgressBar(n_tasks, ipython_notebook)

            if n_tasks is None:
                if type(tasks) is list:
                    n_tasks = len(tasks)
                else:
                    raise (TypeError, "Expected list received %s " % type(tasks))

            if n_workers is None:
                n_workers = multiprocessing.cpu_count() * 4

            pbar.write('Creating %d workers' % n_workers)
            workers = [Worker(tasks_queue, results_queue, **kwargs) for _ in range(n_workers)]

            for w in workers:
                w.start()

            for task in tasks:
                tasks_queue.put(task)
                # pbar.update()

            for w in range(n_workers):
                tasks_queue.put(None)

            for res in range(n_tasks):
                result = results_queue.get()
                if result is not None:
                    results.append(result)
                pbar.update()

            pbar.write('Joining...')
            for w in workers:
                w.join()

            pbar.finish()
        except KeyboardInterrupt:
            os._exit(1)
        except Exception as e:
            print(e)
            raise e
        finally:
            return results
