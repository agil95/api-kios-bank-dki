# ========================================================
# MTKF31 DLL for Python
# ========================================================
class MTKF31Communication:
    def __init__(self):
        self.STX_F31 = '0xF2'  # Start Byte
        self.ETX = '0x03'  # End Byte
        self.ENQ = '0x05'
        self.ACK = '0x06'  # Acknowledgement
        self.NAK = '0x15'  # No Acknowledgement
        self.CMT = '0x43'  # Command Header (‘C’,0x43H)

    def SendF31Command(self, address, cdt1, cdt2):
        # print("command", cdt1)
        textlen = len(cdt1) + 1
        if len(cdt2) != 0:
            textlen += len(cdt2) + 1

        textlentransform = textlen.to_bytes(1, byteorder='big')

        _msgbuff = b''
        _msgbuff += int(self.STX_F31, 16).to_bytes(1, byteorder='big')
        _msgbuff += int(address, 16).to_bytes(1, byteorder='big')
        _msgbuff += (int.from_bytes(textlentransform, byteorder='big') >> 8 & 255).to_bytes(1, byteorder='big')
        _msgbuff += (int.from_bytes(textlentransform, byteorder='big') & 255).to_bytes(1, byteorder='big')
        _msgbuff += int(self.CMT, 16).to_bytes(1, byteorder='big')
        _msgbuff += int(cdt1[0], 16).to_bytes(1, byteorder='big') + int(cdt1[1], 16).to_bytes(1, byteorder='big')
        if len(cdt2) != 0:
            _msgbuff += int(cdt2[0], 16).to_bytes(1, byteorder='big') + int(cdt2[1], 16).to_bytes(1, byteorder='big')
        _msgbuff += int(self.ETX, 16).to_bytes(1, byteorder='big')
        calBcc = self.CalcBCC(_mesg=_msgbuff.hex())
        _msgbuff += calBcc.to_bytes(1, byteorder='big')

        print("[INFO] message to machine =>", _msgbuff)
        return _msgbuff

    def SendACK(self):
        try:
            _mesg = int(self.ACK, 16).to_bytes(1, byteorder='big')
        except Exception as err:
            print("[ERROR] {}".format(err))

    def SendENQ(self):
        try:
            _mesg = int(self.ENQ, 16).to_bytes(1, byteorder='big')
        except Exception as err:
            print("[ERROR] {}".format(err))

    def CalcBCC(self, _mesg):
        print(len(_mesg))
        b = 0
        length = 2
        listBuff = [('0x' + _mesg[i:i + length]) for i in range(0, len(_mesg), length)]
        for i in listBuff:
            b ^= int(i, 16)
        return b


class MTKF31Status:
    # STATUS byte 48 bin 010 NoCardPresent
    # STATUS byte 49 bin 110 CardAtExitSlot
    # STATUS byte 50 bin 210 CardAtReadPos
    status = ['Unknown', 'No Card Present', 'Card at Exit Slot', 'Card at Read Pos']


class MTKF31Command:
    # F2 00 00 03 43 30 33 03 B0        Reset and No Movement
    reset = b'\xF2\x00\x00\x03\x43\x30\x33\x03\xB0'

    # F2 00 00 03 43 30 30 03 B1        Move to Front if card in
    move_card_to_bezel = b'\xF2\x00\x00\x03\x43\x30\x30\x03\xB1'

    # F2 00 00 03 43 30 31 03 B0        Move to Error Card bin if card in
    move_card_error_to_bin = b'\xF2\x00\x00\x03\x43\x30\x31\x03\xB0'

    # F2 00 00 03 43 30 33 03 B2        Only Initialize, retain Card In;
    initialize_retain_card_in = b'\xF2\x00\x00\x03\x43\x30\x33\x03\xB2'

    # F2 00 00 03 43 30 34 03 B5        Move Card To Front and Count;
    move_card_to_front_and_count = b'\xF2\x00\x00\x03\x43\x30\x34\x03\xB5'

    # F2 00 00 03 43 30 35 03 B4        Move Card To Error Card Bin and Count;
    move_card_error_to_bin_and_count = b'\xF2\x00\x00\x03\x43\x30\x35\x03\xB4'

    # F2 00 00 03 43 30 37 03 B6        Retain Card In and Count;
    retain_card_in_and_count = b'\xF2\x00\x00\x03\x43\x30\x37\x03\xB6'

    # F2 00 00 03 43 31 30 03 B0        Current Machine Status
    machine_status = b'\xF2\x00\x00\x03\x43\x31\x30\x03\xB0'

    # F2 00 00 03 43 31 31 03 B1        Sensor Status
    sensor_status = b'\xF2\x00\x00\x03\x43\x31\x31\x03\xB1'

    # F2 00 00 03 43 33 30 03 B2        Enable Insertion
    enable_insertion = b'\xF2\x00\x00\x03\x43\x33\x30\x03\xB2'

    # F2 00 00 03 43 33 31 03 B3        Disable Insertion
    disable_insertion = b'\xF2\x00\x00\x03\x43\x33\x30\x03\xB3'

    # F2 00 00 03 43 32 31 03 B2        Move To IC contact
    move_to_IC = b'\xF2\x00\x00\x03\x43\x32\x31\x03\xB2'

    # F2 00 00 03 43 32 32 03 B1        Move To RF Contact
    move_to_RF = b'\xF2\x00\x00\x03\x43\x32\x32\x03\xB1'

    # F2 00 00 03 43 32 39 03 BA        Eject Card Without Hold
    eject_card = b'\xF2\x00\x00\x03\x43\x32\x39\x03\xBA'

    # F2 00 00 03 43 32 30 03 B3        Issue Card and Hold at front
    dispense_card = b'\xF2\x00\x00\x03\x43\x32\x30\x03\xB3'

    # F2 00 00 03 43 32 33 03 B0        Move Card To Error Card Bin
    retain_card = b'\xF2\x00\x00\x03\x43\x32\x33\x03\xB0'
