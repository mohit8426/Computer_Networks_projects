#!/usr/bin/env python3
'''
Name: Mohit Kulkarni
UTAID: 1002031021
Programming Language : Python
Python Version: 3.8

Main Reference: https://gist.github.com/junian/99e402db918cbe150002dc8c6736feb6
Socket and Threading: https://medium.com/from-the-scratch/http-server-what-do-you-need-to-know-to-build-a-simple-http-server-from-scratch-d1ef8945e4fa
'''
import socket
import time
import threading
import signal
import sys

def Client_Thread(s):
   connect_client, addr = s.accept()  
   print('Client got the connection through',addr,'\n')
   # Creating new thread for the client request, and continuing recieving  connections
   threading.Thread(target=client, args=(connect_client, addr)).start()
   
send_time = time.time()
print("The Sending time of the client is : ",send_time)

#client data recieved and respond
def client(connect_client, addr):
   persist_conn = False
   #While loop to keep listening activity. If you want to exit use clt + c twice
   while True:
      try:
         '''
        began receiving client requests with browser data and various types of data.
         '''
         req_client = connect_client.recv(1024).decode()
         '''
         terminating the inactive connection. 
         If not closed, a large number of threads will be created with out-of-range indexes.
         '''
         receving_time = time.time()
         print("Receiveing Time is : ",receving_time)
         RTT = receving_time - send_time
         print("RTT is :",RTT) # Calculate and Display RTT for the client request5. 

         if not req_client:
            print("Closing the connection for client as there is no active connection!!")
            connect_client.close()
            break
         #Extracting header related data from the recived request
         req_method = req_client.split(' ')[0]     
         http_version = req_client.split('/')[2][:3]
         print("Request Body: \n" + req_client)
         '''
        When using HTTP 1.1, persistent connections stay open until the client quits them, 
        but we must provide a timeout if a header is missing.
         '''        
         if http_version == '1.1' and persist_conn == False:
            persist_conn = True
            connect_client.settimeout(10)
         #Responding to the client using GET operation for the client
         if req_method == "GET":
            '''
           The second position, which has a file 
           name after the localhost, is obtained from the req client object after it 
           has been divided into a list: port
            '''
            req_file = req_client.split()[1]
            # '/' is for the default path to find the html file.
            if req_file == "/":
               req_file = "/index.html"
            #file type at list postion 1
            try:
               #With loop to avoid using closing by explitly mentening it and Sending HTTP response with file content
               with open(req_file.replace("/", ""), 'r') as html:
                 response_data = html.read()
               #Creating header for the html file
               rec_head = resp_header(200, http_version)
               '''
              sending the header and content of the index.html file to the browser.
               '''
               print(rec_head)
               connect_client.send(rec_head.encode() + response_data.encode())
            except Exception as e:
               print("404 File Not Found!!!")
               rec_head = resp_header(404, http_version) # Reciveing header response
               print(rec_head)
               connect_client.send(rec_head.encode())
         else:
            print("ERROR: Other than GET HTTP request method:  " + req_method)
            print("Stoping client socket...")
            connect_client.close()
            break
      # After reaching the connection timeout value the Exception is thrown (http 1.1 - persistent connection)
      except socket.timeout:
         print("The socket connection timeout value is (10 seconds), closing client socket...")
         connect_client.close()
         break
      
# This method generates http response headers depending on the version of the http protocol and the response code
def resp_header(resp_code, http_version):
   header = ''
   current_time = time.strftime("%a, %d %b %Y %H:%M:%S", time.localtime())
   # If http version is 1.0, stop the connection after recieving the response
   if http_version == '1.0':  
      if resp_code == 200:
         header += 'HTTP/1.0 200 OK\n' # it responds this message together with the requested pageto the client.
      if resp_code == 404:
         header += 'HTTP/1.0 404 Not Found\n' # error message if not recieved properly
      header += 'Date: ' + current_time + '\n'
      header += 'Server: MohitK\'s Simple Web Server\n'
      header += 'Connection: close\n'
   # If http version is 1.1, keep connection active after the response from the server
   elif http_version == '1.1':  
      if resp_code == 200:
         header += 'HTTP/1.1 200 OK\n'
      elif resp_code == 404:
         header += 'HTTP/1.1 404 Not Found\n'
      header += 'Date: ' + current_time + '\n'
      header += 'Server: MohitK\'s Simple Web Server\n'
      # Continuity of the connection
      header += 'Connection: keep-alive\n'
      header += 'Content-Type: text/html\n\n'

   return header
   
   

if __name__ == "__main__":
   '''
   The Socket parameter is used to intialize the socket
   object. The internet addr family for IPv4 and sockets is 
   AF INET. The TCP type for stream transfers over networkss
   is called SOCK STREAM.
   '''
   try:
      # Creating the socket and binding it to the port 8086
      socket1 = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
      socket1.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1) 
      print("Socket is Instialised")
      PORT=8086
      socket1.bind(('localhost', PORT))
      print("Binding of the socket to localhostd and "+ str(PORT) + "\n")
      # Have the socket listen for incoming connections
      socket1.listen(4)
      print("Waiting for the connection....")
      while True:
         # Accepting new incoming connections from the client
         Client_Thread(socket1)
   except KeyboardInterrupt:
      print("Interuption accord during keyboard")
   except Exception as e:
      # Printing the exception
      print(e)
      sys.exit()