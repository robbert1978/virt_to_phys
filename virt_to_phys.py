import gdb

GetValue = gdb.parse_and_eval

MAX_U64 = (1 << 64) - 1

PAGE_OFFSET_BASE = 0xffff888000000000

PHYSICAL_MASK = (1 << 46) - 1

PAGE_SIZE = 1 << 12
PAGE_MASK = ~(PAGE_SIZE - 1) & MAX_U64
PHYSICAL_PAGE_MASK = PAGE_MASK & PHYSICAL_MASK

PMD_PAGE_SIZE = 1 << 21
PMD_PAGE_MASK = ~(PMD_PAGE_SIZE - 1) & MAX_U64
PHYSICAL_PMD_PAGE_MASK = PMD_PAGE_SIZE & PHYSICAL_MASK

_PAGE_BIT_PRESENT = 0
_PAGE_BIT_RW = 1
_PAGE_BIT_USER = 2
_PAGE_BIT_ACCESSED = 5
_PAGE_BIT_DIRTY = 6
_PAGE_BIT_NX = 63

_PAGE_PRESENT = 1 << _PAGE_BIT_PRESENT
_PAGE_RW = 1 << _PAGE_BIT_RW
_PAGE_USER = 1 << _PAGE_BIT_USER
_PAGE_ACCESSED = 1 << _PAGE_BIT_ACCESSED
_PAGE_DIRTY = 1 << _PAGE_BIT_DIRTY
_PAGE_NX = 1 << _PAGE_BIT_NX


def Red(skk): return "\033[91m{}\033[00m" .format(skk)
def Green(skk): return "\033[92m{}\033[00m" .format(skk)


class physicAddr (gdb.Command):
    def __init__(self):
        super(physicAddr, self).__init__("physicAddr", gdb.COMMAND_USER)

    def invoke(self, vaddr, from_tty):

        if type(vaddr) == str:
            vaddr = int(vaddr, 16) if "0x" == vaddr[:2] else int(vaddr)
        elif type(vaddr) != int:
            raise TypeError

        PML4_index = (vaddr >> 39) & ((1 << 9) - 1)
        PDPE_index = (vaddr >> 30) & ((1 << 9) - 1)
        PDE_index = (vaddr >> 21) & ((1 << 9) - 1)
        PTE_index = (vaddr >> 12) & ((1 << 9) - 1)
        PAGE_index = vaddr & ((1 << 12) - 1)

        """
        /* Extracts the PFN from a (pte|pmd|pud|pgd)val_t of a 4KB page */
        #define PTE_PFN_MASK		((pteval_t)PHYSICAL_PAGE_MASK)
        """
        PML4_addr = GetValue("$cr3")

        PDPE_addr = GetValue(
            f"*(long long *){hex(PAGE_OFFSET_BASE + PML4_addr + PML4_index*8)}") & PHYSICAL_PAGE_MASK  # PGD

        PDE_addr = GetValue(
            f"*(long long *){hex(PAGE_OFFSET_BASE + PDPE_addr + PDPE_index*8)}") & PHYSICAL_PAGE_MASK  # PMD

        PTE_addr = GetValue(
            f"*(long long *){hex(PAGE_OFFSET_BASE + PDE_addr + PDE_index*8)}") & PHYSICAL_PAGE_MASK  # PTE

        PAGE_addr = GetValue(
            f"*(long long *){hex(PAGE_OFFSET_BASE + PTE_addr + PTE_index*8)}") & PHYSICAL_PAGE_MASK

        info = GetValue(
            f"*(long long *){hex(PAGE_OFFSET_BASE + PTE_addr + PTE_index*8)}") & MAX_U64

        if info & _PAGE_PRESENT:
            info_present = Green("PRESENT")
        else:
            info_present = Red("NOT_PRESENT")

        if info & _PAGE_RW:
            info_rw = Green("RW")
        else:
            info_rw = Red("RO")

        if info & _PAGE_USER:
            info_user = Green("USERMODE")
        else:
            info_user = Red("KERNELMODE")

        if info & _PAGE_ACCESSED:
            info_acessed = Red("ACCESSED")
        else:
            info_acessed = Green("NOT_ACCESSED")

        if info & _PAGE_DIRTY:
            info_dirty = Green("NOT_DIRTY")
        else:
            info_dirty = Red("DIRTY")

        if info & _PAGE_NX:
            info_nx = Green("NX")
        else:
            info_nx = Red("EXECUTABLE")

        print(f"PDPE at {hex(PDPE_addr)}")
        print(f"PDE at {hex(PDE_addr)}")
        print(f"PTE at {hex(PTE_addr)}")
        print(f"PAGE at {hex(PAGE_addr)}")
        print(f"Info: {hex(info)}")
        print(
            f"Info: {info_present}|{info_rw}|{info_user}|{info_acessed}|{info_dirty}|{info_nx}")
        print(f"Physical address = {hex(PAGE_addr + PAGE_index)}")

        gdb.execute(f"tele {hex(PAGE_OFFSET_BASE + PAGE_addr + PAGE_index)}")


physicAddr()
