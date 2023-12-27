def formatting():
    x = []
    with open('red.txt') as f:
        for s in f.read().split(','):
            x.append(s)
    with open('duotoutunshi.txt', 'w') as f:
        for s in x:
            f.write(s.replace(" '", "").replace("'", ""))
            f.write('\n')
formatting()