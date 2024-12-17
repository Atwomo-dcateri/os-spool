import multiprocessing
import queue
import time
import random
import subprocess  # 用于模拟设备驱动（调用lp命令）

BUFFER_SIZE = 5
NUM_PRODUCERS = 3  # 设置生产者进程数量
NUM_CONSUMERS = 2  # 设置消费者进程数量

# 写入日志的函数
def write_log(message):
    with open("task_log.txt", "a") as log_file:
        log_file.write(message + "\n")

# 模拟设备驱动程序（例如模拟调用 lp 命令）
#def simulate_device_print(task_content):
    # 在 Linux 系统中，可以通过 lp 命令模拟打印机操作
    # 这里仅使用 print 模拟设备操作
    #print(f"Simulating printing of: {task_content}")
    #subprocess.call(["lp", task_content]) 
    # 实际操作中，可以执行类似于 subprocess.call(["lp", task_content]) 的命令
    # subprocess.call(["lp", task_content])  # 在系统中调用 lp 打印命令


def simulate_device_processing(task):
    try:
        result = subprocess.run(['lp', task], check=True, capture_output=True, text=True)
        print(f"Simulating printing of: {task}")
    except subprocess.CalledProcessError as e:
        print(f"Error occurred during device simulation: {e}")
        print(f"Simulating printing of: {task} (Fallback)")

# 生产者进程
def producer(queue, lock, stop_event, producer_id, condition):
    task_id = 1
    while not stop_event.is_set():
        time.sleep(random.uniform(0.5, 1.5))  # 模拟生产任务时间
        priority = random.randint(1, 10)  # 随机优先级，数字越小优先级越高
        task = (priority, task_id, f"Task-{task_id}")

        with lock:
            if queue.qsize() >= BUFFER_SIZE:
                log_message = f"[Producer-{producer_id}] Queue is full, waiting... (Task-{task_id})"
                print(log_message)
                write_log(log_message)
                condition.wait()  # 如果队列满了，等待消费者消费任务
            else:
                queue.put(task)
                log_message = f"[Producer-{producer_id}] Added Task-{task_id} with priority {priority}"
                print(log_message)
                write_log(log_message)
                condition.notify_all()  # 通知消费者有新任务可用
                task_id += 1

# 消费者进程
def consumer(queue, lock, stop_event, consumer_id, condition):
    while not stop_event.is_set():
        time.sleep(random.uniform(1.0, 2.0))  # 模拟消费任务时间
        with lock:
            if queue.empty():
                log_message = f"[Consumer-{consumer_id}] Queue is empty, waiting..."
                print(log_message)
                write_log(log_message)
                condition.wait()  # 队列为空时，等待生产者添加任务
            else:
                task = queue.get()
                log_message = f"[Consumer-{consumer_id}] Processing {task[2]} with priority {task[0]}"
                print(log_message)
                write_log(log_message)

                # 执行模拟设备打印
                simulate_device_print(task[2])
                condition.notify_all()  # 通知生产者可以添加任务

if __name__ == "__main__":
    # 使用 PriorityQueue 来根据优先级处理任务
    spool_queue = queue.Queue(BUFFER_SIZE)  # 普通队列
    queue_lock = multiprocessing.Lock()
    stop_event = multiprocessing.Event()  # 用于通知子进程退出
    condition = multiprocessing.Condition(queue_lock)  # 使用 Condition 进行进程间同步

    # 创建并启动多个生产者进程
    producer_processes = []
    for i in range(NUM_PRODUCERS):
        producer_process = multiprocessing.Process(target=producer, args=(spool_queue, queue_lock, stop_event, i+1, condition))
        producer_processes.append(producer_process)
        producer_process.start()

    # 创建并启动多个消费者进程
    consumer_processes = []
    for i in range(NUM_CONSUMERS):
        consumer_process = multiprocessing.Process(target=consumer, args=(spool_queue, queue_lock, stop_event, i+1, condition))
        consumer_processes.append(consumer_process)
        consumer_process.start()

    try:
        # 等待生产者和消费者进程完成
        for producer_process in producer_processes:
            producer_process.join()
        for consumer_process in consumer_processes:
            consumer_process.join()
    except KeyboardInterrupt:
        print("\nTerminating processes...")
        stop_event.set()  # 设置退出信号
        for producer_process in producer_processes:
            producer_process.join()
        for consumer_process in consumer_processes:
            consumer_process.join()
        print("All processes terminated.")


'''
任务优先级：为任务添加优先级队列。
任务日志：将任务的执行记录到文件中。
支持多消费者/多生产者：实现多个生产者或消费者进程的协调。
设备模拟：消费者执行任务时，可以调用设备驱动程序（如通过lp命令实际打印内容）。
'''