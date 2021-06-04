#import main.py

start_n = int(input("Enter Start Number >> "))
start_ls = list()
for i in range(start_n):
    x,y=map(int,input("Enter Start Point >> x y ").split())
    start_ls.append((x,y))

end_n = int(input("Enter End Number >> "))
end_ls = list()
for i in range(end_n):
    x,y=map(int,input("Enter End Point >> x y ").split())
    end_ls.append((x,y))

for s in range(len(start_ls)):
    SetStart(node_list[start_ls[s][0]][start_ls[s][1]])
    print(s)
    for e in range(len(end_ls)):
        SetEnd(node_list[end_ls[e][0]][end_ls[e][1]])
        print(e)
