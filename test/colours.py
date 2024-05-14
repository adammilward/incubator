



class Colours:
    def __init__(self):
        self.END      = '\33[0m'
        self.BOLD     = '\33[1m'
        self.ITALIC   = '\33[3m'
        self.URL      = '\33[4m'
        self.BLINK    = '\33[5m'
        self.BLINK2   = '\33[6m'
        self.SELECTED = '\33[7m'

        self.BLACK  = '\33[30m'
        self.RED    = '\33[31m'
        self.GREEN  = '\33[32m'
        self.YELLOW = '\33[33m'
        self.BLUE   = '\33[34m'
        self.VIOLET = '\33[35m'
        self.CYAN  = '\33[36m'
        self.WHITE  = '\33[37m'

        self.BLACKBG  = '\33[40m'
        self.REDBG    = '\33[41m'
        self.GREENBG  = '\33[42m'
        self.YELLOWBG = '\33[43m'
        self.BLUEBG   = '\33[44m'
        self.VIOLETBG = '\33[45m'
        self.BEIGEBG  = '\33[46m'
        self.WHITEBG  = '\33[47m'

        self.GREY    = '\33[90m'
        self.RED2    = '\33[91m'
        self.GREEN2  = '\33[92m'
        self.YELLOW2 = '\33[93m'
        self.BLUE2   = '\33[94m'
        self.VIOLET2 = '\33[95m'
        self.CYAN2  = '\33[96m'
        self.WHITE2  = '\33[97m'

        self.GREYBG    = '\33[100m'
        self.REDBG2    = '\33[101m'
        self.GREENBG2  = '\33[102m'
        self.YELLOWBG2 = '\33[103m'
        self.BLUEBG2   = '\33[104m'
        self.VIOLETBG2 = '\33[105m'
        self.BEIGEBG2  = '\33[106m'
        self.WHITEBG2  = '\33[107m'

    def output(self):
        print(self.END , 'self.END      = \33[0m', self.END)
        print(self.BOLD , 'self.BOLD     = \33[1m', self.END)
        print(self.ITALIC , 'self.ITALIC   = \33[3m', self.END)
        print(self.URL , 'self.URL      = \33[4m', self.END)
        print(self.BLINK , 'self.BLINK    = \33[5m', self.END)
        print(self.BLINK2 , 'self.BLINK2   = \33[6m', self.END)
        print(self.SELECTED , 'self.SELECTED = \33[7m', self.END)

        print(self.BLACK , 'self.BLACK  = \33[30m', self.END)
        print(self.RED , 'self.RED    = \33[31m', self.END)
        print(self.GREEN , 'self.GREEN  = \33[32m', self.END)
        print(self.YELLOW , 'self.YELLOW = \33[33m', self.END)
        print(self.BLUE , 'self.BLUE   = \33[34m', self.END)
        print(self.VIOLET , 'self.VIOLET = \33[35m', self.END)
        print(self.CYAN , 'self.CYAN  = \33[36m', self.END)
        print(self.WHITE , 'self.WHITE  = \33[37m', self.END)

        print(self.BLACKBG , 'self.BLACKBG  = \33[40m', self.END)
        print(self.REDBG , 'self.REDBG    = \33[41m', self.END)
        print(self.GREENBG , 'self.GREENBG  = \33[42m', self.END)
        print(self.YELLOWBG , 'self.YELLOWBG = \33[43m', self.END)
        print(self.BLUEBG , 'self.BLUEBG   = \33[44m', self.END)
        print(self.VIOLETBG , 'self.VIOLETBG = \33[45m', self.END)
        print(self.BEIGEBG , 'self.BEIGEBG  = \33[46m', self.END)
        print(self.WHITEBG , 'self.WHITEBG  = \33[47m', self.END)

        print(self.GREY , 'self.GREY    = \33[90m', self.END)
        print(self.RED2 , 'self.RED2    = \33[91m', self.END)
        print(self.GREEN2 , 'self.GREEN2  = \33[92m', self.END)
        print(self.YELLOW2 , 'self.YELLOW2 = \33[93m', self.END)
        print(self.BLUE2 , 'self.BLUE2   = \33[94m', self.END)
        print(self.VIOLET2 , 'self.VIOLET2 = \33[95m', self.END)
        print(self.CYAN2 , 'self.CYAN2  = \33[96m', self.END)
        print(self.WHITE2 , 'self.WHITE2  = \33[97m', self.END)

        print(self.GREYBG , 'self.GREYBG    = \33[100m', self.END)
        print(self.REDBG2 , 'self.REDBG2    = \33[101m', self.END)
        print(self.GREENBG2 , 'self.GREENBG2  = \33[102m', self.END)
        print(self.YELLOWBG2 , 'self.YELLOWBG2 = \33[103m', self.END)
        print(self.BLUEBG2 , 'self.BLUEBG2   = \33[104m', self.END)
        print(self.VIOLETBG2 , 'self.VIOLETBG2 = \33[105m', self.END)
        print(self.BEIGEBG2 , 'self.BEIGEBG2  = \33[106m', self.END)
        print(self.WHITEBG2 , 'self.WHITEBG2  = \33[107m', self.END)


        print()
        print(self.YELLOW2, self.REDBG , 'self.YELLOW2, self.REDBG    = \33[41m', self.END)

colours = Colours()
colours.output()

