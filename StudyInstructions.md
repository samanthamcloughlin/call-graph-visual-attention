Welcome!#

Thank you for participating in [elide for double blind] lab's research study. Your participation in this study is voluntary and may end any time you choose. 

The overall aim of this study is to record programmer eye-movements during the completion of a code documentation task. 

The nature of documentation we ask you to generate is contextual, i.e. we wish to learn the **purpose** of a snippet of Java code in context of the project. 

We will ask you to generate 3 sentence descriptions for each method where:

The first sentence should explain the purpose of the method in as simple of terms as possible, in the context of the whole program.

The second should describe the more specific functionalities and under what circumstances they occur. 

The last sentence should describe why this method is needed within the context of the overall project.


For Example:

Method:

    public boolean isNextBatchReady() {
        int count = 0;
        long size = 0;

        clientsLock.lock();
        /******* BEGIN CLIENTS CRITICAL SECTION ******/        
        
        Iterator<Entry<Integer, ClientData>> it = clientsData.entrySet().iterator();

        while (it.hasNext()) {
            ClientData clientData = it.next().getValue();
            
            clientData.clientLock.lock();
            RequestList reqs = clientData.getPendingRequests();
            if (!reqs.isEmpty()) {
                for(TOMMessage msg:reqs) {
                    if(!msg.alreadyProposed) {
                        count++;
                        size += msg.serializedMessage.length;
                    }
                }
            }
            clientData.clientLock.unlock();
        }

        /******* END CLIENTS CRITICAL SECTION ******/
        clientsLock.unlock();
        return count >= controller.getStaticConf().getMaxBatchSize()
                || size >= controller.getStaticConf().getMaxBatchSizeInBytes();
    }


------------------------------------------------------------------------------------------------------------------------------------------------------------
Expected Description: 
The method checks if the next batch of requests from client to server are ready in a smart device.

It  filters requests that are already proposed and returns true if there are enough requests to fill next batch, otherwise returns false.

This method is additionally useful when locking and unlocking the queue for new requests based on the status of the next batch.

------------------------------------------------------------------------------------------------------------------------------------------------------------

Not all the information required to generate this description is present in the code above. We expect you to investigate other methods in the project to generate these descriptions. You may use the Eclipse IDE features like call-graph to aid in this effort. 
 
#Please confirm to your study administrator that you understand the task and ask them any questions you might have before proceeding.

Done? Lets Begin!

#Go to scrimage.txt
