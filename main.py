from rich import print
from zhipuai import ZhipuAI
import zhipuai
import pandas as pd
import threading


def request(beginwith:str):
    # beginwith:按字母开头分析单词
    client = ZhipuAI(api_key="")  # 请填写您自己的APIKey

    propmt="""
    # 角色

    你是一名中英文双语教育专家，拥有帮助将中文视为母语的用户理解和记忆英语单词的专长，请根据用户提供的英语单词完成下列任务。

    ## 任务

    ### 分析词义

    - 系统地分析用户提供的英文单词，并用中文以简单易懂的方式解答；

    ### 列举例句

    - 根据所需，为该单词提供至少 3 个不同场景下的使用方法和例句。并且附上中文翻译，以帮助用户更深入地理解单词意义。

    ### 词根分析

    - 用中文分析并展示单词的词根；
    - 列出由词根衍生出来的其他单词；

    ### 词缀分析

    - 用中文分析并展示单词的词缀，例如：单词 individual，前缀 in- 表示否定，-divid- 是词根，-u- 是中缀，用于连接和辅助发音，-al 是后缀，表示形容词；
    - 列出相同词缀的的其他单词；

    ### 发展历史和文化背景

    - 用中文详细介绍单词的造词来源和发展历史，以及在欧美文化中的内涵

    ### 单词变形

    - 列出单词对应的名词、单复数、动词、不同时态、形容词、副词等的变形以及对应的中文翻译。
    - 列出单词对应的固定搭配、组词以及对应的中文翻译。

    ### 记忆辅助

    - 用中文提供一些高效的记忆技巧和窍门，以更好地记住英文单词。

    ### 小故事

    - 用英文撰写一个有画面感的场景故事，包含用户提供的单词。
    - 要求使用简单的词汇，100 个单词以内。
    - 英文故事后面附带对应的中文翻译。
    """

    df = pd.read_excel('wordlist.xlsx')
    # 提取第一列的内容
    first_column = df.iloc[:, 0]  # iloc[:, 0] 表示选择所有行的第一列
    
    # 收集需要分析的单词
    to_process=list()
    for item in first_column:
        if item[0] != beginwith:
            continue
        else:
            to_process.append(item)
    first_column=to_process
    all_cnt=len(first_column)
    lines=0
    
    # 分析所有以beginwith开头的单词
    for item in first_column:
        try:
            lines+=1
            print(f"{beginwith}:处理第{lines}个/共{all_cnt}个:{item}")
            response = client.chat.completions.create(
            model="glm-4-plus",  # 请填写您要调用的模型名称
            messages=[
                {"role": "system", "content": propmt},
                {"role": "user", "content": item}
            ],
            )
            result=response.choices[0].message.content
            # 写入文件
            with open('./letters/'+beginwith+'.md', 'a',encoding='utf-8') as f:
                f.write('\n---------------\n')
                f.write(f'## {item}\n')
                f.write(result+'\n\n')
        except zhipuai.core._errors.APIRequestFailedError:
            print('敏感词:',item)
        except Exception as e:
            print('未知的异常:',e)

    print(beginwith,'[red]解析完毕[/red]')


if __name__=="__main__":
    # 单词表
    alphabet='abcdefghijklmnopqrstuvwxyz'
    alphabet_list=list(alphabet)
    threads = []
    for letter in alphabet_list:
        # 多线程分别生成 如果提示并发量过大可以把alphabet拆成两半，跑两次代码
        thread = threading.Thread(target=request, args=(letter,), daemon=True)
        threads.append(thread)
        thread.start()
    
    for thread in threads:
        thread.join()