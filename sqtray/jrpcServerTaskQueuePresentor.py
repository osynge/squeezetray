







class jrpcServerTaskQueuePresentor():
    
    def __init__(self, threadpool):
        self.log = logging.getLogger("JrpcServer.SqueezeConnectionThreadPool")
        self.threadpool = threadpool
        
    
        
