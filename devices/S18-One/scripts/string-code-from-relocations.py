'''
This is quick and dirty script to help clean-up relocation entries quickly. It
is quite terrible and will likely not work properly in different versions, and
certainly not different platforms.

This is included for an example of what was done, rather than for any other
reason.
'''

import re
import idautils

s_addr = 0x1071A70
e_addr = 0x107B658
c_addr = s_addr

# Used to cache addresses of strings known to IDA (as int).
string_addrs = {}


def has_string_entry(addr):
    '''
    Check whether the provided address is being tracked by IDA as a string. In
    order to attempt to speed up subsequent lookups, string addresses will be
    cached into a dictionary on first use.

    Data returned will be a dictionary of strings, keyed by the address of the
    string with the length as the value.

    Args:
        addr (int): The address to check.

    Returns:
        A dictionary of string lengths keyed by their address.
    '''
    if len(string_addrs) == 0:
        for s in idautils.Strings():
            string_addrs[s.ea] = s.length

    try:
        return string_addrs[addr]
    except KeyError:
        return None


# Fix relocation table to be qwords, if required.
# while c_addr < e_addr:
#     create_qword(c_addr)
#     c_addr += 0x8

# Get the get src address from each relocation entry and mark it as a qword.
# c_addr = s_addr
# while c_addr < e_addr:
#     src = Qword(c_addr)
#     create_qword(src)
#     c_addr += 0x18

# Mark code sections and strings appropriately, based on whether IDA knows the
# address as a string.
c_addr = s_addr
while c_addr < e_addr:
    candidate = Qword(c_addr+0x10)
    c_addr += 0x18

    # If it looks like a string, mark as a string literal.
    if has_string_entry(candidate):
        if not create_strlit(candidate, candidate + string_addrs[candidate]):
            print('[!] Failed to mark 0x{0:0x} as string'.format(candidate))
        continue

    # Attempt to mark as a procedure, and wait for AA.
    ida_auto.auto_make_proc(candidate)
    ida_auto.auto_wait()

    if not isCode(GetFlags(candidate)):
        print('[!] Failed to mark 0x{0:0x} as code'.format(candidate))

    continue
