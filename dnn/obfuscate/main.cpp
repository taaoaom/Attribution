#include "obfuscate.h"
#include <string>

int main()
{
	srand(time(nullptr));
	obf my_obf;
	printf("Enter file path: ");
	char path[260]="";
	//gets_s(path,260);
	// strcpy_s(path,"D:\\Program\\obfuscate\\Debug\\Project1.exe");
	if(!my_obf.init(path))
	{
		puts("Initialization failed");
		my_obf.print_last_error_string();
		system("pause");
		return -1;
	}
	size_t begin, end;
	printf("Please enter the interval to obfuscate (left-closed right-open, the second number should be the address of the instruction after the last instruction) e.g.: 0x401000 0x402000:\n");  // "请输入要混淆的区间（左闭右开，第二个数应该是最后一条指令的下一条指令的地址）如：0x401000 0x402000:\n"
	//scanf_s("%x %x", &begin, &end);
	//if (!my_obf.obf_begin_set(begin, end))
	int t1=GetTickCount();
	if (!my_obf.obf_begin_set(0x401040, 0x401106))
	{
		puts("obf_begin_set failed"); 
		my_obf.print_last_error_string();
		system("pause");
		return -1;
	}
	
	// for(int i=1;i<=20;++i)
	// {
	// 	printf("%d\n",i);
	// 	my_obf.obf_out_of_order(30);
	// 	my_obf.obf_encrypt_jcc();
	// }
	// for(int i=1;i<=1;++i)
	// {
	// 	printf("%d\n",i);
	// 	my_obf.obf_out_of_order(30);
	// 	my_obf.obf_vector_jmp();
	// }
	// my_obf.obf_out_of_order(30);

	// for(int i=1;i<=10;++i)
	// {
	// 	printf("%d\n",i);
	// 	my_obf.obf_out_of_order(50);
	//  	my_obf.obf_vector_jmp();
	// 	my_obf.obf_equivalent_variation();
	// }

	//jmp_label_by_retn bug
	
	my_obf.obf_no_jcc();
	//my_obf.obf_equivalent_variation();
	
	puts("Equivalent variation");
	for(int i=1;i<=20;++i){
		printf("%d\n",i);
		my_obf.obf_equivalent_variation();
	}
	puts("Dead code insertion");
	for(int i=1;i<=5;++i){
		printf("%d\n",i);
		my_obf.obf_local_obf();
	}
	puts("Code disorder");
	for(int i=1;i<=5;++i)
	{
		printf("%d\n",i);
		my_obf.obf_out_of_order(50);
		my_obf.obf_vector_jmp();
	}
	for(int i=1;i<=3;++i)
	{
		printf("%d\n",i);
		my_obf.obf_out_of_order(50);
	}

	my_obf.obf_end_set();
	if(!my_obf.add_section(".obf",my_obf.m_binary_buffer, my_obf.m_size))
	{
		puts("Adding section failed");
		system("pause");
		return -1;
	}
	if(!my_obf.save_file())
	{
		puts("File save failed");
		system("pause");
		return -1;
	}
	puts("File saved successfully");
	int t2=GetTickCount();
	printf("Time taken: %.2f seconds\n", (t2 - t1)/1000.0);
	system("pause");
	return 0;
}
