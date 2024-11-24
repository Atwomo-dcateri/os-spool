import multiprocessing
import time
import random

# 定义SPOOL区的缓冲区大小
BUFFER_SIZE = 5

# 生产者进程
def producer(queue, lock):
    task_id = 1
    while True:
        time.sleep(random.uniform(0.5, 1.5))  # 模拟生产任务时间
        task = f"Task-{task_id}"  # 模拟任务内容
        with lock:  # 确保互斥访问队列
            if queue.full():
                print("[Producer] Queue is full, waiting...")
            else:
                queue.put(task)
                print(f"[Producer] Added {task} to the queue.")
                task_id += 1

# 消费者进程
def consumer(queue, lock):
    while True:
        time.sleep(random.uniform(1.0, 2.0))  # 模拟消费任务时间
        with lock:  # 确保互斥访问队列
            if queue.empty():
                print("[Consumer] Queue is empty, waiting...")
            else:
                task = queue.get()
                print(f"[Consumer] Processed {task}")

if __name__ == "__main__":
    # 使用多进程的队列和锁
    spool_queue = multiprocessing.Queue(BUFFER_SIZE)
    queue_lock = multiprocessing.Lock()
    stop_event = multiprocessing.Event()

    # 创建生产者和消费者进程
    producer_process = multiprocessing.Process(target=producer, args=(spool_queue, queue_lock))
    consumer_process = multiprocessing.Process(target=consumer, args=(spool_queue, queue_lock))

    # 启动进程
    producer_process.start()
    consumer_process.start()

    # 主进程等待子进程运行
    try:
        producer_process.join()
        consumer_process.join()
    except KeyboardInterrupt:
        print("\nTerminating processes...")
        stop_event.set()
        producer_process.terminate()
        consumer_process.terminate()
