from crypt import methods
from dataclasses import dataclass
from flask import Blueprint, render_template, request, jsonify
from flask_cors import cross_origin
from sqlalchemy import Date, cast
from datetime import datetime, timedelta
from project.models import LogUang, LogTicket, LogPeron, Config, Pengaduan
from project import db
from project.dll.MTKF31_dll import MTKF31Command, MTKF31Status
from escpos.printer import Usb
from time import sleep

import usb.core
import usb.util
import json
import serial
import codecs
import subprocess
import re
import os


api = Blueprint('api', __name__, url_prefix='/api')
img_dir = './project/static/assets/img/'
logo_header = os.path.join(img_dir, 'logo-bank-header.jpg')
logo_bank_dki = os.path.join(img_dir, 'logo-bank-dki-res.jpeg')
logo_kaliadem = os.path.join(img_dir, 'logo-kaliadem.jpeg') 


def device_io(port, baudrate, stopbits, timeout):
    ser = serial.Serial(
        port=port,
        baudrate=baudrate,
        bytesize=serial.EIGHTBITS,
        parity=serial.PARITY_NONE,
        stopbits=stopbits,
        timeout=timeout,
    )
    return ser

    
def response_io(result, info):
    if ser.is_open:
        original = codecs.encode(result, 'hex').decode().upper()
        indexing = [(original[i:i + 2]) for i in range(0, len(original), 2)]
        output = " ".join([(original[i:i + 2])
                          for i in range(0, len(original), 2)])
        print(info, output)
        return indexing
    else:
        print('[INFO] Port is close!')


def vendor_product():
    device_re = re.compile(b"Bus\s+(?P<bus>\d+)\s+Device\s+(?P<device>\d+).+ID\s(?P<id>\w+:\w+)\s(?P<tag>.+)$", re.I)
    df = subprocess.check_output("lsusb")
    devices = []
    for i in df.split(b'\n'):
        if i:
            info = device_re.match(i)
            if info:
                dinfo = info.groupdict()
                dinfo['device'] = '/dev/bus/usb/%s/%s' % (dinfo.pop('bus'), dinfo.pop('device'))
                devices.append(dinfo)
            
    return devices


def format_rupiah(uang):
    y = str(uang)
    if len(y) <= 3:
        return y
    else:
        p = y[-3:]
        q = y[:-3]
        return format_rupiah(q) + '.' + p


def test_print_struk(idvendor, idproduct, image):
    try:
        p = Usb(idVendor=idvendor, idProduct=idproduct, timeout=0, in_ep=0x81, out_ep=0x03)
        p.open()
        p.initialize()
        # p.leftMargin(leftMargin=100)
        p.image(image)
        p.control(ctl="FF")
        p.cut(mode="PART")
        p.close()
        return 'Ok'
    except Exception as e:
        return str(e)


def print_struk_ticket(idvendor, idproduct, idtransaction, berangkat, typetransaction, penumpang, ticketprice, kapal, vmid):
    waktu = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
    # save to db
    # store_data(idtransaction, typetransaction, cardname, waktu, cardprice)
    # ready to print
    print("|─────────────────────────────────────────|")
    print("|    Jaket Boat                           |")
    print("|    Jakarta e-Ticketing Boat             |")
    print("|    (+62) 822-7800-780                   |")
    print("|    Penumpang                            |")
    print("|    {}                                 |".format(penumpang))
    print("|    ==================================   |")
    print("|    Kode          :  #{}            |".format(idtransaction))
    print("|    Berangkat     :  {}             |".format(berangkat))
    print("|    Harga         :  Rp.{}            |".format(format_rupiah(str(ticketprice))))
    print("|                                         |")
    print("|    Kapal {}                   |".format(kapal))
    print("|    VM Id         : {}         |".format(vmid))
    print("|─────────────────────────────────────────|")
  
    try:
        p = Usb(idVendor=idvendor, idProduct=idproduct, timeout=0, in_ep=0x81, out_ep=0x03)
        p.open()
        p.initialize()
        # p.leftMargin(leftMargin=100)
        p.set(align="center", font='a', text_type='B', width=2, height=2)
        p.text('Jaket Boat')
        p.lf()
        p.set(align="center", font='b', text_type='normal')
        p.text('Jakarta e-Ticketing Boat')
        p.lf()
        p.text('(+62) 822-7800-780')
        p.lf()
        p.text('Penumpang')
        p.lf()
        p.set(align="center", font='b', text_type='B')
        p.text(penumpang)
        p.lf()
        # p.text('=======================================')
        # p.tabPositions([3, 24])
        p.lf()
        p.set(align="left", font='a', text_type='B')
        p.text('\tKode')
        p.tab()
        p.tab()
        p.text(idtransaction)
        p.lf()
        p.text('\tBerangkat')
        p.tab()
        p.text(berangkat)
        p.lf()
        p.text('\tHarga')
        p.tab()
        p.tab()
        p.text('Rp. ' + format_rupiah(str(ticketprice)))
        p.lf()
        p.lf()
        p.set(align="center")
        p.qr(str(idtransaction), size=7)
        p.lf()
        p.set(align="center", font='b', text_type='normal')
        p.text(kapal)
        p.lf()
        p.text('VM Id: ' + vmid)
        p.lf()
        p.lf()
        p.control(ctl="PF")
        # p.control(ctl="FF")
        p.cut(mode="PART")
        p.close()

        return 'Ok'
    except Exception as e:
        return str(e)


def print_struk_peron(idvendor, idproduct, customer, peronprice, quantity, total, ticketscode, createdat, vmid):
    global p
    waktu = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
    # ready to print
    print("|─────────────────────────────────────────|")
    print("|    Jaket Boat                           |")
    print("|    Jakarta e-Ticketing Boat             |")
    print("|    (+62) 822-7800-780                   |")
    print("|                                         |")
    print("|    Peron                                |")
    print("|    ==================================   |")
    print("|    Kode          :  #{}            |".format(ticketscode[0]))
    print("|    Tanggal       :  {}             |".format(createdat))
    print("|    Harga         :  Rp.{}            |".format(format_rupiah(str(peronprice))))
    print("|                                         |")
    print("|                                         |")
    print("|    VM Id         : {}         |".format(vmid))
    print("|─────────────────────────────────────────|")
   
    try:
        p = Usb(idVendor=idvendor, idProduct=idproduct, timeout=0, in_ep=0x81, out_ep=0x03)
        p.open()
        for code in ticketscode:
            p.initialize()
            # p.leftMargin(leftMargin=100)
            p.image(logo_bank_dki, high_density_vertical=True, high_density_horizontal=True, impl='bitImageRaster', fragment_height=960, center=False)
            p.set(align="center", font='a', text_type='B', width=2, height=2)
            p.text('Jaket Boat')
            p.lf()
            p.set(align="center", font='b', text_type='normal')
            p.text('Jakarta e-Ticketing Boat')
            p.lf()
            p.text('(+62) 822-7800-780')
            p.lf()
            p.lf()
            p.set(align="center", font='a', text_type='B')
            p.text('Peron')
            p.lf()
            # p.text('=======================================')
            # p.tabPositions([3, 24])
            p.lf()
            p.set(align="left", font='a', text_type='B')
            p.text('\tKode ')
            p.tab()
            p.tab()
            p.text(code)
            p.lf()
            p.text('\tTanggal')
            p.tab()
            p.tab()
            p.text(createdat)
            p.lf()
            p.text('\tHarga')
            p.tab()
            p.tab()
            p.text('Rp. ' + format_rupiah(str(peronprice)))
            p.lf()
            p.lf()
            p.set(align="center")
            p.qr(code, size=7)
            p.lf()
            p.set(align="center", font='b', text_type='normal')
            p.lf()
            p.text('VM Id: ' + vmid)
            p.lf()
            p.lf()
            p.control(ctl="PF")
            # p.control(ctl="FF")
            p.cut(mode="PART")
        p.close()

        return 'Ok'
    except Exception as e:
        return str(e)


def print_struk_pengaduan(idvendor, idproduct, customerid, vmid, name, ticketprice, moneyaccept, moneychanges, 
                           description):
    waktu = datetime.now().strftime("%d/%m/%Y %H:%M")
    # ready to print
    print("|──────────────────────────────────────────────|")
    print("|    Jaket Boat                                |")
    print("|    Jakarta e-Ticketing Boat                  |")
    print("|    (+62) 822-7800-780                        |")
    print("|                                              |")
    print("|    Pengaduan                                 |")
    print("|    ======================================    |")
    print("|    Kode Pelanggan        :  {}               |".format(customerid))
    print("|    Nama Lengkap          :  {}               |".format(name))
    print("|    Harga Tiket           :  Rp.{}            |".format(format_rupiah(str(ticketprice))))
    print("|    Total Uang Masuk      :  Rp.{}            |".format(format_rupiah(str(moneyaccept))))
    print("|                          ----------------    |")
    print("|    Total Uang Kembalian  :  Rp.{}            |".format(format_rupiah(str(moneychanges))))
    print("|                                              |")
    print("|    Keterangan                                |")
    print("|    ======================================    |")
    print("|    {}                                        |".format(description))
    print("|                                              |")
    print("|    VM ID: {} | {}                            |".format(vmid, waktu))
    print("|──────────────────────────────────────────────|")
    try:
        p = Usb(idVendor=idvendor, idProduct=idproduct, timeout=0, in_ep=0x81, out_ep=0x03)
        p.open()
        p.initialize()
        p.leftMargin(leftMargin=50)
        p.set(align="left", font='a', text_type='B', width=2, height=2)
        p.text('Jaket Boat')
        p.lf()
        p.set(align="left", font='b', text_type='normal')
        p.text('Jakarta e-Ticketing Boat')
        p.lf()
        p.text('(+62) 822-7800-780')
        p.lf()
        p.lf()
        p.set(align="left", font='a', text_type='B')
        p.text('Pengaduan')
        p.lf()
        p.set(align="left", font='b', text_type='normal')
        p.text('========================================================')
        p.lf()
        p.set(align="left", font='a', text_type='B')
        p.text('Kode Pelanggan')
        p.tab()
        p.tab()
        p.text(customerid)
        p.lf()
        p.text('Nama Lengkap')
        p.tab()
        p.tab()
        p.text(name)
        p.lf()
        p.text('Harga Tiket')
        p.tab()
        p.tab()
        p.text('Rp. ' + format_rupiah(str(ticketprice)))
        p.lf()
        p.text('Total Uang Masuk')
        p.tab()
        p.text('Rp. ' + format_rupiah(str(moneyaccept)))
        # if ticketprice != moneyaccept:
        #     p.lf()
        #     p.set(align="left", font='b', text_type='normal')
        #     # p.text('                         ---------------------')
        #     # p.text('---------------------------------------')
        #     p.lf()
        #     p.lf()
        #     p.set(align="left", font='a', text_type='B')
        #     p.text('Total Uang yg harus dikembalikan:')
        #     p.lf()
        #     p.text('Rp. ' + format_rupiah(str(moneychanges)))
        p.lf()
        p.lf()
        p.set(align="left", font='a', text_type='B')
        p.text('Keterangan:')
        p.set(align="left", font='b', text_type='normal')
        p.lf()
        p.text(description)
        p.lf()
        p.lf()
        p.text(f'VM Id: {vmid} @ {waktu}')
        p.lf()
        p.set(align="left", font='b', text_type='normal')
        p.text('*Serahkan bukti tiket kepada petugas.')
        p.lf()
        p.lf()
        p.control(ctl="PF")
        # p.control(ctl="FF")
        p.cut(mode="PART")
        p.close()

        return 'Ok'
    except Exception as e:
        return str(e)


def insert_log_money(money, customerId):
    global status, verify_at, description
    try:
        status = "SUCCESS"
        verify_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        description = "Uang Masuk"
        new_log = LogUang(id=0, customer=customerId, income=money,
                        status=status, verify_at=verify_at,
                        description=description)
        db.session.add(new_log)
        db.session.commit()
        print("[INFO] Success insert money log!")

    except Exception as e:
        print(f"[INFO] Failed insert money log -> {str(e)}")


def delete_log_money():
    LogUang.query.delete()
    db.session.commit()
    print("[INFO] Successfully delete money log!")


def insert_log_ticket(ref_number, booking_code, passanger_code, passanger, origin, departure_at, destination, 
                    arrive_at, status, price, money_changes, description, paid_at, ticket_type):
    try:
        new_log = LogTicket(id=0, ref_number=ref_number, booking_code=booking_code,
                                passanger_code=passanger_code, passanger=passanger, 
                                origin=origin, departure_at=departure_at, 
                                destination=destination, arrive_at=arrive_at,
                                status=status, price=price, money_changes=money_changes, 
                                description=description, paid_at=paid_at, ticket_type=ticket_type)
        db.session.add(new_log)
        db.session.commit()      
        print("[INFO] Success insert ticket log!")

    except Exception as e:
        print(f"[INFO] Failed insert ticket log -> {str(e)}")


def insert_log_peron(ref_number, customer, peron_price, quantity, total, status, tickets_code, 
                     money_changes, created_at):
    try:
        new_log = LogPeron(ref_number=ref_number, customer=customer,
                            peron_price=peron_price, quantity=quantity, 
                            total=total, status=status, 
                            tickets_code=tickets_code, money_changes=money_changes, 
                            created_at=created_at)
        db.session.add(new_log)
        db.session.commit()      
        print("[INFO] Success insert peron log!")

    except Exception as e:
        print(f"[INFO] Failed insert peron log -> {str(e)}")


def insert_pengaduan(customer_id, vm_id, name, ticket_price, money_accept, money_changes, answer_status,
                    description, created_at, updated_at):
    try:
        new_pengaduan = Pengaduan(customer_id=customer_id, vm_id=vm_id, name=name,
                                ticket_price=ticket_price, money_accept=money_accept, 
                                money_changes=money_changes, answer_status=answer_status,                             
                                description=description, created_at=created_at, updated_at=updated_at)
        db.session.add(new_pengaduan)
        db.session.commit()      
        print("[INFO] Success insert pengaduan!")

    except Exception as e:
        print(f"[INFO] Failed insert pengaduan -> {str(e)}")


def cancel_money_validator():
    global ser
    cmdSync = bytes.fromhex("7F 80 01 11 65 82")
    cmdHostProtocolVersion7 = bytes.fromhex("7F 80 02 06 07 21 94")
    cmdDisable = bytes.fromhex("7F 80 01 09 35 82")
    ser = device_io(port='/dev/ttyUSB0', baudrate=9600,
                   stopbits=serial.STOPBITS_TWO, timeout=1)
    if ser.is_open:
        ser.write(cmdSync)
        sleep(0.5)
        ser.write(cmdHostProtocolVersion7)
        sleep(0.5)
        ser.write(cmdDisable)
        ser.flush()
        ser.close()

        return True
    else:
        return False

# ============================================================================================================== #

@api.route('/test', methods=['POST'])
def test():
    data = request.get_json()
    test = data.get('ticket_price')
    print(test)
    return jsonify({'test': test})


@api.route('/money_validator', methods=['POST'])
def money_validator():
    global ser, holdinEscrow, transactionType, price, customerId, moneyChanges

    # generic command
    cmdSync = bytes.fromhex("7F 80 01 11 65 82")
    cmdSetupRequest = bytes.fromhex("7F 80 01 05 1D 82")
    cmdSetupRequest_alt = bytes.fromhex("7F 00 01 05 1E 08 ")
    cmdSetGenerator = bytes.fromhex(
        "7F 80 09 4A C5 05 8F 3A 00 00 00 00 B2 73")
    cmdSetModulus = bytes.fromhex("7F 80 09 4B 8D A6 13 00 00 00 00 00 6C F6")
    cmdHostProtocolVersion6 = bytes.fromhex("7F 80 02 06 06 24 14")
    cmdHostProtocolVersion6_alt = bytes.fromhex("7F 00 02 06 06 1B 94")
    cmdHostProtocolVersion7 = bytes.fromhex("7F 80 02 06 07 21 94")
    cmdHostProtocolVersion7_alt = bytes.fromhex("7F 00 02 06 07 1E 14")
    cmdGetSerialNumber = bytes.fromhex("7F 80 01 0C 2B 82")
    cmdGetSerialNumber_alt = bytes.fromhex("7F 00 01 0C 28 08 ")
    cmdSetInhibits = bytes.fromhex("7F 80 03 02 FF FF 25 A4")
    cmdSetInhibits_alt = bytes.fromhex("7F 00 03 02 FF FF 26 18")
    cmdSetInhibitsOpen5k10k20k = bytes.fromhex("7F 80 03 02 1C 00 2B EC")
    cmdSetInhibitsOpen5k10k20k_alt = bytes.fromhex("7F 00 03 02 1C 00 28 50")
    cmdSetInhibitsOpen5k10k20k50k100k = bytes.fromhex(
        "7F 80 03 02 7C 00 2E 2C")
    cmdSetInhibitsOpen5k10k20k50k100k_alt = bytes.fromhex(
        "7F 00 03 02 7C 00 2D 90")
    cmdEnable = bytes.fromhex("7F 80 01 0A 3F 82")
    cmdEnable_alt = bytes.fromhex("7F 00 01 0A 3C 08")
    cmdPoll = bytes.fromhex("7F 80 01 07 12 02")
    cmdPoll_alt = bytes.fromhex("7F 00 01 07 11 88")
    cmdReset = bytes.fromhex("7F 80 01 01 06 02")
    cmdReset_alt = bytes.fromhex("7F 00 01 01 05 88")
    cmdDisable = bytes.fromhex("7F 80 01 09 35 82")
    cmdDisable_alt = bytes.fromhex("7F 00 01 09 36 08")
    cmdRejectNote = bytes.fromhex("7F 80 01 08 30 02")
    cmdRejectNote_alt = bytes.fromhex("7F 00 01 08 33 88")
    cmdHold = bytes.fromhex("7F 80 01 18 53 82")
    cmdHold_alt = bytes.fromhex("7F 00 01 18 50 08")

    # ResponeIO command
    cmdResponeIOOk = bytes.fromhex('F0')
    cmdResponeIONotKnown = bytes.fromhex('F2')
    cmdResponeIOWrongParameters = bytes.fromhex('F3')
    cmdResponeIOParametersOutOfRange = bytes.fromhex('F4')
    cmdResponeIOCannotProcess = bytes.fromhex('F5')
    cmdResponeIOSoftwareError = bytes.fromhex('F6')
    cmdResponeIOFail = bytes.fromhex('F8')
    cmdResponeIOKeyNotSet = bytes.fromhex('FA')

    # poll command
    cmdPollSlaveReset = bytes.fromhex('F1')
    cmdPollReadNote = bytes.fromhex('EF')
    cmdPollCreditNote = bytes.fromhex('EE')
    cmdPollNoteRejecting = bytes.fromhex('ED')
    cmdPollNoteRejected = bytes.fromhex('EC')
    cmdPollNoteStacking = bytes.fromhex('CC')
    cmdPollNoteStacked = bytes.fromhex('EB')
    cmdPollStackerFull = bytes.fromhex('E7')
    cmdPollDisabled = bytes.fromhex('E8')
    cmdPollUnsafeNoteJam = bytes.fromhex('E9')
    cmdPollSafeNoteJam = bytes.fromhex('EA')
    cmdPollTimeout = bytes.fromhex('D9')
    cmdPollJammed = bytes.fromhex('D5')

    # body = request.json
    holdinEscrow = False
    customerId = request.get_json().get('customer_id')
    transactionType = request.get_json().get('transaction_type')

    currValue = 0
    tempValue = []
    totalValue = 0
    moneyChanges = 0
    price = request.get_json().get('ticket_price')
    ticketValue = price
    print(f"[INFO] ticket price -> {price} IDR")
    # return jsonify({'test': price})
    # pass

    ser = device_io(port='/dev/ttyUSB0', baudrate=9600,
                   stopbits=serial.STOPBITS_TWO, timeout=1)

    if ser.is_open:
        print("[INFO] Bill validator is Open!")
        # time.sleep(1)
        ser.write(cmdSync)
        res = ser.readline()
        response_io(result=res, info="[INFO] device sync ->")

        sleep(0.5)
        ser.write(cmdHostProtocolVersion7)

        if transactionType == "Buy":
            sleep(1)
            ser.write(cmdSetInhibits_alt)
        else:
            sleep(1)
            ser.write(cmdSetInhibitsOpen5k10k20k50k100k_alt)

        sleep(0.5)
        ser.write(cmdEnable)
        res3 = ser.readline()
        response_io(result=res3, info="[INFO] enable ->")

        if holdinEscrow:
            sleep(1)
            ser.write(cmdHold)
            res4 = ser.readline()
            response_io(result=res4, info="hold in escrow ->")

        print("[INFO] please insert the cash...")
        while currValue < price:
            # Poll 1 -----------------------------------------------------------------------------------------------
            sleep(0.5)
            ser.write(cmdPoll_alt)
            res = ser.readline()
            # ResponeIO(result=res, info="[INFO] poll ResponeIO 1 ->")
            value_one = response_io(
                result=res, info="[INFO] poll ResponeIO 1 ->")
            # time.sleep(1)
            # print("len data 1 ->", len(value_one))
            if len(value_one) > 8:
                if value_one[6] == "EF":
                    if value_one[7] == "07":
                        currValue = 100000
                        tempValue.append(currValue)
                    elif value_one[7] == "06":
                        currValue = 50000
                        tempValue.append(currValue)
                    elif value_one[7] == "05":
                        currValue = 20000
                        tempValue.append(currValue)
                    elif value_one[7] == "04":
                        currValue = 10000
                        tempValue.append(currValue)
                    elif value_one[7] == "03":
                        currValue = 5000
                        tempValue.append(currValue)
                    elif value_one[7] == "02":
                        currValue = 2000
                        tempValue.append(currValue)
                    elif value_one[7] == "01":
                        currValue = 1000
                        tempValue.append(currValue)
                    insert_log_money(money=currValue, customerId=customerId)
                    print('[INFO] cash detect : {} IDR'.format(currValue))
                    print('[INFO] temp cash -> {}'.format(tempValue))
                    totalValue += currValue

                    if totalValue > price:
                        moneyChanges += totalValue - price
                        totalValue = sum(tempValue)
                        print("[INFO] cash is bigger than card price! [poll 1]")
                        # sleep(1)
                        # ser.write(cmdRejectNote)
                        # if len(tempValue) > 2:
                        #     tempValue.pop(-1)
                        #     totalValue = sum(tempValue)
                        # else:
                        #     totalValue = tempValue[0]
                        #     tempValue.pop(-1)
                        #     totalValue = sum(tempValue)
                        print('[INFO] total cash : {} IDR'.format(totalValue))
                        # self.signalMoneyCount.emit(tempValue)
                    else:
                        print('[INFO] total cash : {} IDR'.format(totalValue))
                        # self.signalMoneyCount.emit(tempValue)

                if (value_one[3] + value_one[4]).upper() == "F0ED":
                    print('[INFO] cash ejected!')
                    sleep(0.5)
                    ser.write(cmdRejectNote)

                if (value_one[3] + value_one[4]).upper() == "F0EE":
                    if (value_one[3] + value_one[4] + value_one[6]).upper() == "F0EEEB":
                        print("[INFO] credit cash")
                        print("[INFO] cash stacked")
                        if totalValue >= price:
                            break
                    else:
                        print("[INFO] credit cash")

                if (value_one[3] + value_one[4]).upper() == "F0CC":
                    print("[INFO] cash stacking")

                if (value_one[3] + value_one[4]).upper() == "F0EB":
                    print("[INFO] cash stacked")
                    if totalValue >= price:
                        break

                if (value_one[3] + value_one[4]).upper() == "F0E7":
                    print("[INFO] stacker full!")
                    sleep(1)
                    ser.write(cmdRejectNote)

            else:
                if value_one[5] != "00":
                    if value_one[3] + value_one[4].upper() == "F0EF":
                        if value_one[5] == "07":
                            currValue = 100000
                            tempValue.append(currValue)
                        elif value_one[5] == "06":
                            currValue = 50000
                            tempValue.append(currValue)
                        elif value_one[5] == "05":
                            currValue = 20000
                            tempValue.append(currValue)
                        elif value_one[5] == "04":
                            currValue = 10000
                            tempValue.append(currValue)
                        elif value_one[5] == "03":
                            currValue = 5000
                            tempValue.append(currValue)
                        elif value_one[5] == "02":
                            currValue = 2000
                            tempValue.append(currValue)
                        elif value_one[5] == "01":
                            currValue = 1000
                            tempValue.append(currValue)
                        insert_log_money(money=currValue, customerId=customerId)
                        print('[INFO] cash detect : {}'.format(currValue))
                        print('[INFO] temp cash -> {}'.format(tempValue))
                        totalValue += currValue

                        if totalValue > price:
                            moneyChanges += totalValue - price
                            totalValue = sum(tempValue)
                            print(
                                "[INFO] cash is bigger than card price! [poll 1]")
                            # sleep(1)
                            # ser.write(cmdRejectNote)
                            # if len(tempValue) > 2:
                            #     tempValue.pop(-1)
                            #     totalValue = sum(tempValue)
                            # else:
                            #     totalValue = tempValue[0]
                            #     tempValue.pop(-1)
                            #     totalValue = sum(tempValue)
                            print('[INFO] total cash : {} IDR'.format(totalValue))
                            # self.signalMoneyCount.emit(tempValue)
                        else:
                            print(
                                '[INFO] total cash -> {} IDR'.format(totalValue))
                            # self.signalMoneyCount.emit(tempValue)

                if (value_one[3] + value_one[4]).upper() == "F0ED":
                    print('[INFO] cash ejected!')
                    sleep(0.5)
                    ser.write(cmdRejectNote)

                if (value_one[3] + value_one[4]).upper() == "F0EE":
                    if (value_one[3] + value_one[4] + value_one[6]).upper() == "F0EEEB":
                        print("[INFO] credit cash")
                        print("[INFO] cash stacked")
                        if totalValue >= price:
                            break
                    else:
                        print("[INFO] credit cash")

                if (value_one[3] + value_one[4]).upper() == "F0CC":
                    print("[INFO] cash stacking")

                if (value_one[3] + value_one[4]).upper() == "F0EB":
                    print("[INFO] cash stacked")
                    if totalValue >= price:
                        break

                if (value_one[3] + value_one[4]).upper() == "F0E7":
                    print("[INFO] stacker full!")
                    sleep(1)
                    ser.write(cmdRejectNote)
            # ------------------------------------------------------------------------------------------------------
            # Poll 2 -----------------------------------------------------------------------------------------------
            sleep(0.5)
            ser.write(cmdPoll)
            res2 = ser.readline()
            # ResponeIO(result=res2, info="[INFO] poll ResponeIO 2 ->")
            value_two = response_io(
                result=res2, info="[INFO] poll ResponeIO 2 ->")
            # time.sleep(1)
            # print("len data 2 ->", len(value_two))
            if len(value_two) <= 8:
                if value_two[5] != "00":
                    if value_two[3] + value_two[4].upper() == "F0EF":
                        if value_two[5] == "07":
                            currValue = 100000
                            tempValue.append(currValue)
                        elif value_two[5] == "06":
                            currValue = 50000
                            tempValue.append(currValue)
                        elif value_two[5] == "05":
                            currValue = 20000
                            tempValue.append(currValue)
                        elif value_two[5] == "04":
                            currValue = 10000
                            tempValue.append(currValue)
                        elif value_two[5] == "03":
                            currValue = 5000
                            tempValue.append(currValue)
                        elif value_two[5] == "02":
                            currValue = 2000
                            tempValue.append(currValue)                                                                   
                        elif value_two[5] == "01":
                            currValue = 1000
                            tempValue.append(currValue)
                        insert_log_money(money=currValue, customerId=customerId)
                        print('[INFO] cash detect : {} IDR'.format(currValue))
                        print('[INFO] temp cash -> {}'.format(tempValue))
                        totalValue += currValue

                        if totalValue > price:
                            moneyChanges += totalValue - price
                            totalValue = sum(tempValue)
                            # sleep(0.5)
                            # ser.write(cmdRejectNote)
                            print(
                                "[INFO] cash is bigger than card price! [poll 2]")
                            # if len(tempValue) > 2:
                            #     tempValue.pop(-1)
                            #     totalValue = sum(tempValue)
                            # else:
                            #     totalValue = tempValue[0]
                            #     tempValue.pop(-1)
                            #     totalValue = sum(tempValue)
                            print('[INFO] total cash : {} IDR'.format(totalValue))
                            # self.signalMoneyCount.emit(tempValue)
                        else:
                            print('[INFO] total cash : {} IDR'.format(totalValue))
                            # self.signalMoneyCount.emit(tempValue)

                if (value_two[3] + value_two[4]).upper() == "F0ED":
                    print('[INFO] cash ejected!')
                    sleep(0.5)
                    ser.write(cmdRejectNote_alt)

                if (value_two[3] + value_two[4]).upper() == "F0EE":
                    if (value_two[3] + value_two[4] + value_two[6]).upper() == "F0EEEB":
                        print("[INFO] credit cash")
                        print("[INFO] cash stacked")
                        if totalValue >= price:
                            break
                    else:
                        print("[INFO] credit cash")

                if (value_two[3] + value_two[4]).upper() == "F0CC":
                    print("[INFO] cash stacking")

                if (value_two[3] + value_two[4]).upper() == "F0EB":
                    print("[INFO] cash stacked")
                    if totalValue >= ticketValue:
                        break

                if (value_two[3] + value_two[4]).upper() == "F0E7":
                    print("[INFO] stacker full!")
                    sleep(0.5)
                    ser.write(cmdRejectNote_alt)

            else:
                if value_two[6] == "EF":
                    if value_two[7] == "07":
                        currValue = 100000
                        tempValue.append(currValue)
                    elif value_two[7] == "06":
                        currValue = 50000
                        tempValue.append(currValue)
                    elif value_two[7] == "05":
                        currValue = 20000
                        tempValue.append(currValue)
                    elif value_two[7] == "04":
                        currValue = 10000
                        tempValue.append(currValue)
                    elif value_two[7] == "03":
                        currValue = 5000
                        tempValue.append(currValue)
                    elif value_two[7] == "02":
                        currValue = 2000
                        tempValue.append(currValue)
                    elif value_two[7] == "01":
                        currValue = 1000
                        tempValue.append(currValue)
                        # currValue = 2000
                        # tempValue.append(currValue)
                    insert_log_money(money=currValue, customerId=customerId)
                    print('[INFO] cash detect : {} IDR'.format(currValue))
                    print('[INFO] temp cash -> {}'.format(tempValue))
                    totalValue += currValue

                    if totalValue > price:
                        moneyChanges += totalValue - price
                        totalValue = sum(tempValue)
                        # sleep(0.5)
                        # ser.write(cmdRejectNote)
                        print("[INFO] cash is bigger than card price! [poll 2]")
                        # if len(tempValue) > 2:
                        #     tempValue.pop(-1)
                        #     totalValue = sum(tempValue)
                        # else:
                        #     totalValue = tempValue[0]
                        #     tempValue.pop(-1)
                        #     totalValue = sum(tempValue)
                        print('[INFO] total cash : {} IDR'.format(totalValue))
                        # self.signalMoneyCount.emit(tempValue)
                    else:
                        print('[INFO] total cash : {} IDR'.format(totalValue))
                        # self.signalMoneyCount.emit(tempValue)

                if (value_two[3] + value_two[4]).upper() == "F0ED":
                    print('[INFO] cash ejected!')
                    sleep(0.5)
                    ser.write(cmdRejectNote_alt)

                if (value_two[3] + value_two[4]).upper() == "F0EE":
                    if (value_two[3] + value_two[4] + value_two[6]).upper() == "F0EEEB":
                        print("[INFO] credit cash")
                        print("[INFO] cash stacked")
                        if totalValue >= price:
                            break
                    else:
                        print("[INFO] credit cash")

                if (value_two[3] + value_two[4]).upper() == "F0CC":
                    print("[INFO] cash stacking")

                if (value_two[3] + value_two[4]).upper() == "F0EB":
                    print("[INFO] cash stacked")
                    if totalValue >= price:
                        break

                if (value_two[3] + value_two[4]).upper() == "F0E7":
                    print("[INFO] stacker full!")
                    sleep(0.5)
                    ser.write(cmdRejectNote_alt)

            currValue = 0

            # if totalValue > price:
            #     sleep(0.5)
            #     ser.write(cmdRejectNote)

        # print("---------------------------")
        # print("succesfully card purchased!")
        sleep(0.5)
        ser.write(cmdDisable)
        ser.flush()
        ser.close()
        response_data = {"moneys": tempValue, "money_changes": moneyChanges}
        
        # del tempValue[:]
        # self.signalTransaction.emit('Success')
        return jsonify({'success': True, "message": "Successfully ticket purchased!", "data": response_data}), 200
    else:
        print("[INFO] Bill validator is Close!")
        return jsonify({'success': False, "message": "Bill validator is Close!"}), 500


@api.route('/get_money', methods=['GET'])
def get_money():
    try:
        log = LogUang.query.order_by(LogUang.verify_at.desc()).first()
        if log:
            data = {
                "from": log.customer,
                "message": log.income,
                "status": log.status,
                "time": log.verify_at
            }
            delete_log_money()
            return jsonify({"success": True, "data": data}), 200
        else:
            return jsonify({"success": False, "data": {}, "message": f"No money found"}), 200

    except Exception as e:
        return jsonify({"success": False, "data": {}, "message": str(e)}), 500


@api.route('/delete_money', methods=['DELETE'])
def delete_money():
    delete_log_money()


@api.route('/cancel_transaction', methods=['GET'])
def cancel_transaction():
    response = cancel_money_validator()
    if response:
        return jsonify({'success': True, 'message': 'Success cancel transaction.'}), 200
    else:
        return jsonify({'success': False, 'message': 'Failed cancel bill transaction.'}), 500


@api.route('/print_ticket', methods=['POST'])
def print_ticket():
    data = ["0x0519", "0x2013"]
    idVendor = int(data[0], 16)
    idProduct = int(data[1], 16)
    refNumber = request.get_json().get('ref_number')
    bookingCode = request.get_json().get('booking_code')
    passengerCode = request.get_json().get('passenger_code')
    passengerName = request.get_json().get('passenger_name')
    origin = request.get_json().get('origin')
    departureAt = request.get_json().get('departure_at')
    destination = request.get_json().get('destination')
    arriveAt = request.get_json().get('arrive_at')
    price = request.get_json().get('total_amount')
    moneyChanges = request.get_json().get('money_changes')
    ship = request.get_json().get('ship')
    departure = request.get_json().get('departure')
    status = request.get_json().get('status')
    description = request.get_json().get('description')
    paidAt = request.get_json().get('paid_at')
    ticketType = request.get_json().get('ticket_type')
    vmId = request.get_json().get('vm_id')
    adminFee = request.get_json().get('admin_fee')
    ticketPrice = request.get_json().get('ticket_price')
    result = print_struk_ticket(idvendor=idVendor, idproduct=idProduct, idtransaction=passengerCode, 
                        berangkat=str(departure).replace('-', '/'), typetransaction="Buy", penumpang=passengerName, 
                        ticketprice=price, kapal=ship, vmid=vmId)
    insert_log_ticket(ref_number=refNumber, booking_code=bookingCode, passanger_code=passengerCode, 
                        passanger=passengerName, origin=origin, departure_at=datetime.strptime(departureAt,  "%d-%m-%Y %H:%M"),
                        destination=destination, arrive_at=datetime.strptime(arriveAt,  "%d-%m-%Y %H:%M"), status=status, price=price, 
                        money_changes=moneyChanges, description=description, paid_at=datetime.strptime(paidAt,  "%d-%m-%Y %H:%M"),
                        ticket_type=ticketType)
    if result == 'Ok':
        return jsonify({'success': True, 'message': 'Berhasil cetak tiket :)'}), 200
    else:
        return jsonify({'success': False, 'message': result}), 500


@api.route('/print_ticket_peron', methods=['POST'])
def print_ticket_peron():
    data = ["0x0519", "0x2013"]
    idVendor = int(data[0], 16)
    idProduct = int(data[1], 16)
    vmId = request.get_json().get('vm_id')
    refNumber = request.get_json().get('ref_number')
    customerId = request.get_json().get('customer')
    peronPrice = request.get_json().get('peron_price')
    totalAmount = request.get_json().get('total_amount')
    quantity = request.get_json().get('quantity')
    status = request.get_json().get('status')
    ticketsCode = request.get_json().get('tickets_code')
    createdAt = request.get_json().get('created_at')
    moneyChanges = request.get_json().get('money_changes')
    result = print_struk_peron(idvendor=idVendor, idproduct=idProduct, customer=customerId, peronprice=peronPrice, 
                                quantity=quantity, total=totalAmount, ticketscode=ticketsCode, 
                                createdat=str(createdAt).replace('-', '/'), vmid=vmId)
    insert_log_peron(ref_number=refNumber, customer=customerId, peron_price=peronPrice, quantity=quantity, total=totalAmount, 
                    status=status, tickets_code=ticketsCode, money_changes=moneyChanges, 
                    created_at=datetime.strptime(createdAt,  "%d-%m-%Y %H:%M"))

    if result == 'Ok':
        return jsonify({'success': True, 'message': 'Berhasil cetak tiket peron :)'}), 200
    else:
        return jsonify({'success': False, 'message': result}), 500


@api.route('/complaint', methods=['POST'])
def complaint():
    data = ["0x0519", "0x2013"]
    idVendor = int(data[0], 16)
    idProduct = int(data[1], 16)
    customerId = request.get_json().get('customer_id')
    vmId = request.get_json().get('vm_id')
    name = request.get_json().get('name')
    ticketPrice = request.get_json().get('ticket_price')
    moneyAccept = request.get_json().get('money_accept')
    moneyChanges = request.get_json().get('money_changes')
    description = request.get_json().get('description')
    time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    result = print_struk_pengaduan(idvendor=idVendor, idproduct=idProduct, customerid=str(customerId).upper(), vmid=vmId, name=name, 
                                    ticketprice=ticketPrice, moneyaccept=moneyAccept, moneychanges=moneyChanges, 
                                    description=description)
    insert_pengaduan(customer_id=str(customerId).upper(), vm_id=vmId, name=name, ticket_price=ticketPrice, money_accept=moneyAccept, 
                    money_changes=moneyChanges, answer_status="PENDING", description=description, created_at=time, 
                    updated_at=time)
    if result == 'Ok':
        return jsonify({'success': True, 'message': 'Berhasil cetak tiket pengaduan :)'}), 200
    else:
        return jsonify({'success': False, 'message': customerId}), 500


@api.route('/power_off', methods=['GET'])
def power_off():
    sudo_password = '123456'
    command = 'poweroff'.split()

    try:
        p = subprocess.Popen(['sudo', '-S'] + command, stdin=subprocess.PIPE, stderr=subprocess.PIPE,
                universal_newlines=True)
        sudo_prompt = p.communicate(sudo_password + '\n')[1]
        return jsonify({'success': True, 'message': 'System is shutting down...'}), 200
    except Exception as e:
        return jsonify({'success': False, 'message': 'Failure to shutdown the system...'}), 500


@api.route('/restart', methods=['GET'])
def restart():
    sudo_password = '123456'
    command = 'reboot'.split()
    
    try:
        p = subprocess.Popen(['sudo', '-S'] + command, stdin=subprocess.PIPE, stderr=subprocess.PIPE,
                universal_newlines=True)
        sudo_prompt = p.communicate(sudo_password + '\n')[1]
        return jsonify({'success': True, 'message': 'System is restarting...'}), 200
    except Exception as e:
        return jsonify({'success': False, 'message': 'Failure restarting system...'}), 500


@api.route('/test_print', methods=['GET'])
def test_print():
    data = ["0x0519", "0x2013"]
    idVendor = int(data[0], 16)
    idProduct = int(data[1], 16)
    
    test = test_print_struk(idvendor=idVendor, idproduct=idProduct, image=logo_header)
    if test == 'Ok':
        return jsonify({'success': True, 'message': 'test print ok'}), 200
    else:
        return jsonify({'success': False, 'message': test}), 500