import socket
import threading
from threading import Thread
import json
from collections import OrderedDict
import copy

def start_server(address, backlog):
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    sock.bind(address)
    sock.listen(backlog)
    while True:
        client_sock, client_addr = sock.accept()
        #stream/socket uniquely identified by its addr
        #accepts json string containing orders in the specified format
        #accept: {"Header":int,"Lines": {string:int}}
        t = Thread(target=inv_handler, args=(client_sock, client_addr))
        t.daemon = True
        t.start()

def inv_handler(csock, caddr):
    global ordersmap
    # create unique stream ID
    addr, cid = caddr
    unique_cid = addr.replace(".","") + str(cid)
    
    headers = set()
    breaking_out = False
    while not breaking_out:
        req = csock.recv(1024)
        if not req:            
            break
        
        # validate input json
        try:
            ijson = json.loads(str(req.decode('utf-8')))
        except Exception as e:
            csock.send("Invalid request".encode('utf-8'))
            breaking_out = True
            break

        #get the header and lines from input
        header = ijson['Header']
        if not header:
            csock.send("Header not specified".encode('utf-8'))
            breaking_out = True
            break

        header = str(header)        
        if header in headers:
            csock.send("Duplicate order received".encode('utf-8'))
            breaking_out = True
            break
        
        headers.add(header)
        map_id = unique_cid + "-" + header
        
        lines = ijson['Lines']
        if not lines:
            csock.send("No orders specified".encode('utf-8'))
            breaking_out = True
            break

        lines = OrderedDict(lines)
        for order in lines.items():
            item, qty = order
            if int(qty) not in range(6):
                csock.send("Order quantity is invalid. It should be between 0 and 5".encode('utf-8'))
                breaking_out = True
                break                
            
            with threading.Lock():
                # if all inv is over it is time to say so                
                if sum(inv.values()) == 0:
                    out = ""
                    for key, value in ordersmap.items():
                        key = key.split("-")
                        stream_id = key[0]
                        hdr = key[1]
                        #out += "Stream: {}".format(stream_id)
                        order_out = OrderedDict()
                        allocated = OrderedDict()
                        bo_out = OrderedDict()
                        for item in value:
                            # value is list of orders sublist
                            # each sublist represent required snapshot
                            order_snap = item[0]
                            inv_snap = item[1]
                            bo_inv_snap = item[2]                            
                            for ikey in inv_snap.keys():
                                if ikey in order_snap:
                                    order_out[ikey] = order_snap[1]
                                elif ikey not in order_out:
                                    order_out[ikey] = 0
                                else:
                                    pass
                                
                                if ikey in order_snap and order_snap[1] <= inv_snap[ikey]:
                                    allocated[ikey] = order_snap[1]
                                elif ikey in order_snap and order_snap[1] > inv_snap[ikey]:
                                    allocated[ikey] = inv_snap[ikey]
                                elif ikey not in allocated:
                                    allocated[ikey] = 0
                                else:
                                    pass

                                if ikey in bo_inv_snap:
                                    bo_out[ikey] = bo_inv_snap[ikey]
                                elif ikey not in bo_out:
                                    bo_out[ikey] = 0
                                else:
                                    pass
                                
                        out += "\n{}-{} : {} :: {} :: {} \n".format(stream_id, hdr, list(order_out.values()), list(allocated.values()), list(bo_out.values()))
                    
                    resp = str(out).encode('utf-8') + b'\n'
                    csock.send(resp)
                    breaking_out = True
                    break

                # process order
                preup_inv = copy.deepcopy(inv)
                inventory.update_inventory(str(item), int(qty))
                
                # register sequence order was received in, and
                # we need snapshot of order:inventory:backorder
                # to refer on print
                om_value = [order, preup_inv, copy.deepcopy(backorder_inventory)]
                if map_id not in ordersmap:
                    ordersmap[map_id] = [om_value]
                else:
                    ordersmap[map_id].append(om_value)
                
        resp = str("Processed Stream: {}-{} Header: {}".format(addr, cid, header)).encode('utf-8') + b'\n'
        csock.send(resp)
        
    print("Connection closed", unique_cid)
    
class inventory():
    global inv        
    
    def __init__(self, item, qty):
        inv[item] = qty

    @classmethod
    def update_inventory(self, ordered_item, ordered_qty):
        global backorder_inventory
        backorder_inventory = {}
        available_qty = inv[ordered_item]        
        
        if available_qty > ordered_qty:
            # easy, process it
            inv[ordered_item] = available_qty - ordered_qty
        else:
            backordered_qty =  0
            # allocate remaining inventory
            if available_qty > 0:
                backordered_qty = ordered_qty - available_qty
                inv[ordered_item] = 0
            else:
                backordered_qty = ordered_qty

            # put rest in backorder with updated backorder qty
            if ordered_item in backorder_inventory:
                #keep adding new orders to back ordered
                backorder_inventory[ordered_item] = backorder_inventory[ordered_item] + backordered_qty
            elif backordered_qty > 0:
                backorder_inventory[ordered_item] = backordered_qty
            else:
                pass

if __name__== '__main__':
    # dict to hold current inventory status
    global inv
    inv = OrderedDict()
    # dict to keep orders as they are received to output when inventory reaches zero
    global ordersmap
    ordersmap = OrderedDict()
    
    print('Initializing inventory')
#     inventory("A", 150)
#     inventory("B", 150)
#     inventory("C", 100)
#     inventory("D", 100)
#     inventory("E", 200)
    # sample test data
    inventory("A", 2)
    inventory("B", 3)
    inventory("C", 1)
    inventory("D", 0)
    inventory("E", 0)
    print('Starting inventory service to process orders')
    start_server(('localhost', 7050), 5)
