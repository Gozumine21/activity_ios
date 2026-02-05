print("私は、銀河の歴史に名を残す牛頭峰一です！")
x=1000000
print(type(x))
name = '牛頭峰一'
age = 46
height = 175.5
print(f'私の名前は{name}で、年齢{age}歳で、身長は{height}cmです。')
name = input('あなたの名前を入力して下さい>>')
print('おお'+ name + 'よ、そなたが来るのを待っていたぞ！')
price = int(input('料金を入力して下さい>>'))
number = int(input('人数を入力してください>>'))
payment = int(price/number)
print('お支払いは{}円です'.format(payment))
scores = [88, 90, 95]
total = sum(scores)
avg = total/ len(scores)
print(f'合計{total}点、平均{avg}点')
a= [10, 20, 30, 40, 50]
print(a[1:3])
print(a[2:])
print(a[:3])
print(a[-1])
print(a[-2])
scores={'network:60','database:80','security:50'}
print(scores)
scores={'network':60,'database':80,'security':50}
print(scores['database'])
a = [1, 2, 3]
b = [4, 5, 6]
c = [a, b]
print(c)
print(c[0])
print(c[1][2])
scores = []
scores.append(int(input('国語の点数 >>')))
scores.append(int(input('算数の点数 >>')))
scores.append(int(input('理科の点数 >>')))
scores.append(int(input('社会の点数 >>')))
scores.append(int(input('英語の点数 >>')))
print(f'合計{sum(scores)}点　平均{sum(scores) / len(scores)}点')
name = input('貴方の名前を教えてください>>')
print(f'{name}さん、こんにちわ')
food = input(f'{name}さんの好きな食べ物を教えて下さい>>')
if  food == 'カレー':
    print('素敵です、カレーは最高ですよね')
else:
    print(f'私も{food}が好きですよ')
scores =[80, 100, 20, 60]
if 100 in scores:
    print('100点満点の試験があったんですね、おめでとう！')
else:
    print('次はどれか1つでも100点満点を取ろう')
print('全ての質問にyまたはnで答えて下さい')
okane_aruka = input('お金に余裕はありますか？>>')
if okane_aruka == 'y':
    onaka_suiteruka = input('お腹がすごく空きましたか？>>')
    nomitai_kibunka = input('ビールを飲みたい気分ですか？>>')
if onaka_suiteruka == 'y' and nomitai_kibunka =='y':
    print('焼肉はいかがですか？')
elif onaka_suiteruka == 'y':
    print('カレーはいかがですか')
elif nomitai_kibunka == 'y':
    print('焼き鳥はいかがですか')
else:
    print('パスタはいかがですか')
yashoku_iruka = input('夜食は必要ですか？>>')
if yashoku_iruka == 'y':
    print('コンビニのチキンはいかがですか')
else:
    print('家で食べましょう')
is_awake = True
count = 0
while is_awake == True:
    count += 1
    print(f'ひつじが{count}匹')
    key = input('もう眠りそうですか？(y/n) >>')
    if key == 'y':
        is_awake = False
print('お休みなさい')
scores = [80, 20, 75, 60]
count = 0
while count < len(scores):
    if scores[count] >= 60:
        print('合格')
    else:
        print('不合格')
    count +=1
    scores = [80, 20, 75, 60]
    for data in scores:
        if data >= 60:
            print('合格')
    else:
            print('不合格')