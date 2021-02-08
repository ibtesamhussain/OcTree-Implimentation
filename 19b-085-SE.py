class Pigmentation(object):
    
    def __init__(self, red=0, green=0, blue=0, alpha=None):
    
        self.red = red
        self.green = green
        self.blue = blue
        self.alpha = alpha



class OctreeNode(object):


    def __init__(self, level, parent):

        self.pigmentation = Pigmentation(0, 0, 0)
        self.pixelcount = 0
        self.paletteindex = 0
        self.children = [None]*8
        # add node to current level
        if level < OctreeQuantizer.MAX_DEPTH - 1:
            parent.addlevelnode(level, self)

    def isleaf(self):
        if self.pixelcount > 0:
            return True
        return False

    def getleafnodes(self):
 
        leafnodes = []
        a=True
        b=0
        while a==True:
            
            
            node = self.children[b]
            if node:
                if node.isleaf():
                    leafnodes.append(node)
                else:
                    leafnodes.extend(node.getleafnodes())
            b+=1
            if b==8:
                a=False
        return leafnodes

    def getnodespixelcount(self):
 
        sumcount = self.pixelcount
        for i in range(8):
            node = self.children[i]
            if node:
                sumcount += node.pixelcount
        return sumcount

    def addpigmentation(self, pigmentation, level, parent):
  
        if level >= OctreeQuantizer.MAX_DEPTH:
            self.pigmentation.red += pigmentation.red
            self.pigmentation.green += pigmentation.green
            self.pigmentation.blue += pigmentation.blue
            self.pixelcount += 1
            return
        index = self.getcolorindexforlevel(pigmentation, level)
        if not self.children[index]:
            self.children[index] = OctreeNode(level, parent)
        self.children[index].addpigmentation(pigmentation, level + 1, parent)

    def palette_index(self, pigmentation, level):
 
        if self.isleaf():
            return self.paletteindex
        index = self.getcolorindexforlevel(pigmentation, level)
        if self.children[index]:
            return self.children[index].palette_index(pigmentation, level + 1)
        else:
         
            for i in range(8):
                if self.children[i]:
                    return self.children[i].palette_index(pigmentation, level + 1)

    def removeleaves(self):
  
        result = 0
        for i in range(8):
            node = self.children[i]
            if node:
                self.pigmentation.red += node.pigmentation.red
                self.pigmentation.green += node.pigmentation.green
                self.pigmentation.blue += node.pigmentation.blue
                self.pixelcount += node.pixelcount
                result += 1
        return result - 1

    def getcolorindexforlevel(self, pigmentation, level):
  
        index = 0
        mask = 0x80 >> level
        if pigmentation.red & mask:
            index |= 4
        if pigmentation.green & mask:
            index |= 2
        if pigmentation.blue & mask:
            index |= 1
        return index

    def getcolor(self):
   
        return Pigmentation(
            self.pigmentation.red / self.pixelcount,
            self.pigmentation.green / self.pixelcount,
            self.pigmentation.blue / self.pixelcount)


class OctreeQuantizer(object):

    MAX_DEPTH = 8

    def __init__(self):
 
        self.levels = {i: [] for i in range(OctreeQuantizer.MAX_DEPTH)}
        self.root = OctreeNode(0, self)

    def getleaves(self):
   
        return [node for node in self.root.getleafnodes()]

    def addlevelnode(self, level, node):
    
        self.levels[level].append(node)

    def addpigmentation(self, pigmentation):
   
      
        self.root.addpigmentation(pigmentation, 0, self)

    def makepalette(self, pigmentationcount):
 
        palette = []
        paletteindex = 0
        leafcount = len(self.getleaves())
     
        for level in range(OctreeQuantizer.MAX_DEPTH - 1, -1, -1):
            if self.levels[level]:
                for node in self.levels[level]:
                    leafcount -= node.removeleaves()
                    if leafcount <= pigmentationcount:
                        break
                if leafcount <= pigmentationcount:
                    break
                self.levels[level] = []
    
        for node in self.getleaves():
            if paletteindex >= pigmentationcount:
                break
            if node.isleaf():
                palette.append(node.getcolor())
            node.paletteindex = paletteindex
            paletteindex += 1
        return palette

    def palette_index(self, pigmentation):
        return self.root.palette_index(pigmentation, 0)





from PIL import Image
def main():
    picture = Image.open('3.jpg')
    pixels = picture.load()
    width, height = picture.size

    octree = OctreeQuantizer()

    for j in range(height):
        for i in range(width):
            octree.addpigmentation(Pigmentation(*pixels[i, j]))

    palette = octree.makepalette(55)

    palettepicture = Image.new('RGB', (256, 256))
    palettepixels = palettepicture.load()
    for i, pigmentation in enumerate(palette):
        palettepixels[i % 16, i / 16] = (int(pigmentation.red), int(pigmentation.green), int(pigmentation.blue))
    palettepicture.save('3_palette.jpg')

    resultpicture = Image.new('RGB', (width, height))
    resultpixels = resultpicture.load()
    for j in range(height):
        
        for i in range(width):
            index = octree.palette_index(Pigmentation(*pixels[i, j]))
            pigmentation = palette[index]
            resultpixels[i, j] = (int(pigmentation.red), int(pigmentation.green), int(pigmentation.blue))
    resultpicture.save('3_result.jpg')


if __name__ == '__main__':
    main()
