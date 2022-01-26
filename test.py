from PIL import Image 
import imagehash

hash = imagehash.average_hash(Image.open('./img2/default.jpg')) 

otherhash = imagehash.average_hash(Image.open('./img/cam.jpg')) 

print(hash - otherhash)