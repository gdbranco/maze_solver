import os
import sys
import logging
import imageio
from pprint import pprint
from PIL import Image

logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')
#https://stackoverflow.com/questions/12995434/representing-and-solving-a-maze-given-an-image
class MazeSolver:
    def __init__(self, maze_path):
        self.path = maze_path
        self.tmp_dir = os.path.join("./tmp", os.path.basename(self.path).split('.')[0] + "/")
        self.DIR_OUT = "./Results"
        self.DIR_IN = "./mazes"
        if not os.path.exists(self.DIR_OUT):
            os.mkdir(self.DIR_OUT)
            logging.info("Diretorio de saida criado {}".format(self.DIR_OUT))
        if not os.path.exists(self.tmp_dir):
            logging.info("Diretorio temporario criado {}".format(self.tmp_dir))
            os.makedirs(self.tmp_dir)
        ext = self.path.split('.')[-1]            
        self.file_in = os.path.join(self.DIR_IN, os.path.basename(self.path))
        self.file_out = os.path.join(self.DIR_OUT, os.path.basename(self.path).split('.')[0] + '.' + ext)
        self.colors = {
            "red": (255, 0, 0),
            "green": (0, 255, 0),
            "blue": (0, 0, 255),
            "white": (255, 255, 255),
            "black": (0, 0, 0)
        }
        self.start_color = self.colors["green"]
        self.end_color = self.colors["red"]
        self.paint = self.colors["blue"]
        self.SNAP = 10000
        self.image = Image.open(self.file_in)
        self.image = self.image.convert('RGB')
        self.pixels = self.image.load()
        self.START = (400,984)
        self.END = (398,25)
        logging.info("Imagem carregada '{}' ({} pixels)".format(self.path,self.image.size))

    def purifyImage(self,save=False):
        limit = 256/2 #cores vao de 0 a 255, logo 128 é a metade
        width,height = self.image.size
        res_pixels = self.pixels
        for i in range(width):
            for j in range(height):
                red,green,blue = self.pixels[i,j]
                if red > limit and green > limit and blue > limit:
                    res_pixels[i,j] = self.colors["white"]
                else:
                    res_pixels[i,j] = self.colors["black"]
        if save:
            self.pixelsToImage(self.image.size,res_pixels,self.path.split('.')[0] + "_pure.jpeg")
        return res_pixels

    def pixelsToImage(self,size,pixels,file_out):
        out = Image.new("RGB", size)
        _pixels = out.load()
        for i in range(size[0]):
            for j in range(size[1]):
                _pixels[i,j] = pixels[i,j]
        out.save(file_out)
        logging.info("Imagem pura salva '{}' ({} pixels)".format(file_out,out.size))

    def show(self,image):
        image.show()

    def solve(self,pure_pixels):
        logging.info('Resolvendo...')
        path = self.BFS(self.START,self.END,pure_pixels)
        if path is None:
            logging.error("Nenhum caminho encontrado")
            self.color(self.START,self.start_color)
            self.color(self.END,self.end_color)
        else:
            for position in path:
                x,y = position
                self.pixels[x,y] = self.colors['red']
        self.image.save(self.file_out)
        logging.info("Solução salva como '{}'".format(self.file_out))

    def BFS(self,START,END,pure_pixels):
        image = self.image.copy()
        pixels = image.load()
        iter = 0
        Q = [[START]]
        visited = dict()
        size = image.size
        for i in range(size[0]):
            for j in range(size[1]):
                visited[(i,j)] = 0
        img = 0
        while len(Q) != 0:
            path = Q.pop(0)
            pos = path[-1]
            visited[pos] = 1
            #Achou um caminho
            if pos==END:
                return path
            neighbors = self.neighbors(pos)
            for neighbor in neighbors:
                x,y = neighbor
                #Se estiver dentro e for branco(caminho)
                if self.inBound(image.size,x,y) and self.isWhite(pixels[x,y]) and not visited[neighbor]:
                    pixels[x,y] = self.paint
                    new_path = list(path)
                    new_path.append(neighbor)
                    Q += [new_path]
                if iter % self.SNAP == 0:
                    image.save('{}/{}.jpeg'.format(self.tmp_dir,img))
                    img+=1
                iter+=1
        return None
    def color(self,pos,color=(255,0,0)):
        x,y = pos
        d = 10
        for i in range(-d,d):
            self.pixels[x+i,y] = color
        for i in range(-d,d):
            self.pixels[x,y+i] = color
    def inBound(self,size,x,y):
        mx,my = size
        if x < 0 or y < 0  or x>=mx or y >=my:
            return False
        return True
    def isWhite(self,value):
        if value == self.colors['white']:
            return True
        return False
    def neighbors(self,pos):
        x,y = pos
        return [(x-1,y),(x,y-1),(x+1,y),(x,y+1)]
    def genGIF(self):
        filenames = os.listdir(self.tmp_dir)
        for item in filenames:
            im = Image.open(self.tmp_dir + item)
            imResize = im.resize((int(im.size[0]/4),int(im.size[1]/4)), Image.ANTIALIAS)
            imResize.save(self.tmp_dir + item,'JPEG', quality=100)
        filenames.sort(key= lambda x: float(x.strip('.jpeg')))
        images = []
        for filename in filenames:
            images.append(imageio.imread(self.tmp_dir + filename))
        imageio.mimwrite(self.DIR_OUT + "/" + self.path.split(".")[0] + ".gif", images)
        logging.info("GIF BFS criada")
if __name__ == "__main__":
    SOLVER = MazeSolver("maze1.jpg")
    pure = SOLVER.purifyImage()
    SOLVER.solve(pure)
    SOLVER.genGIF()