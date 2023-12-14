# Script converts virtual address to physical address

Assuming that the kernel uses 4-level paging, and [`_page_offset_base` is `0xffff888000000000`](https://elixir.bootlin.com/linux/v5.15/source/arch/x86/include/asm/page_64_types.h#L42)

![image](https://github.com/robbert1978/virt_to_phys/assets/31349426/8e69d0af-c333-4cb4-ad01-d418a4eb12a7)
