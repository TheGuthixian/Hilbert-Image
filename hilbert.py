from PIL import Image, ImageOps
from math import floor

counter = 0

def hilbert_spectrum(image_file, degree=4):
    try:
        image = Image.open(image_file)
    except IOError as er:
        return er, '\nImage file not found'
    grey_image = image.convert("L")
    squared_image = square_hilbert_image(grey_image, image_file, degree)
    spectrum = [0 for x in range(int((2**degree)**2))]
    # print(spectrum, len(spectrum))
    h_spectrum = recurrent_hilbert_to_spectrum(squared_image, spectrum)
    return h_spectrum


def square_hilbert_image(image, filename='example.jpg', degree=6):
    # long_side = max(image.size)
    square_width = 2**degree
    horisontal_padding = (square_width-image.size[0])/2
    vertical_padding = (square_width-image.size[1])/2

    image2 = image.crop(
        (
            -horisontal_padding,
            -vertical_padding,
            image.size[0]+horisontal_padding,
            image.size[1]+vertical_padding

        )
    )

    image2.save('squared_hilbert_{}_{}'.format(degree, filename))
    return image2


def recurrent_hilbert_to_spectrum(image, spectrum):
    if image.size[0] == 2:

        data = list(image.getdata())
        data = [data[offset:offset+2] for offset in range(0, 4, 2)]
        # print(spectrum, data)
        spectrum[0] = data[1][0]
        spectrum[1] = data[0][0]
        spectrum[2] = data[0][1]
        spectrum[3] = data[1][1]
        return spectrum
    else:
        image1 = ImageOps.mirror(image.crop((0, image.size[1]/2, image.size[0]/2, image.size[1])).rotate(90))
        image2 = image.crop((0, 0, image.size[0]/2, image.size[1]/2))
        image3 = image.crop((image.size[0]/2, 0, image.size[0], image.size[1]/2))
        image4 = ImageOps.mirror(image.crop((image.size[0]/2, image.size[1]/2, image.size[0], image.size[1])).rotate(-90))

        first_square = floor(len(spectrum)/4)
        second_square = floor(len(spectrum)/2)
        third_square = floor(3*len(spectrum)/4)
        # fourth_square = len(spectrum)-1

        spectrum[:first_square] = recurrent_hilbert_to_spectrum(
            image1, spectrum[:first_square])
        spectrum[first_square:second_square] = recurrent_hilbert_to_spectrum(
            image2, spectrum[first_square:second_square])
        spectrum[second_square:third_square] = recurrent_hilbert_to_spectrum(
            image3, spectrum[second_square:third_square])
        spectrum[third_square:] = recurrent_hilbert_to_spectrum(
            image4, spectrum[third_square:])

        return spectrum


def hilbert_image(spectrum, filename='example.jpg'):
    image = reccurent_hilbert_to_image(spectrum)
    image.save(filename)


def reccurent_hilbert_to_image(spectrum):
    if len(spectrum) == 4:
        return hilbert_image_segment(spectrum)
    else:
        first_square = floor(len(spectrum) / 4)
        second_square = floor(len(spectrum) / 2)
        third_square = floor(3 * len(spectrum) / 4)
        # fourth_square = len(spectrum)-1
        spectrum1 = spectrum[:first_square]
        spectrum2 = spectrum[first_square:second_square]
        spectrum3 = spectrum[second_square:third_square]
        spectrum4 = spectrum[third_square:]

        image1 = ImageOps.mirror(reccurent_hilbert_to_image(spectrum1).rotate(90))
        image2 = reccurent_hilbert_to_image(spectrum2)
        image3 = reccurent_hilbert_to_image(spectrum3)
        image4 = ImageOps.mirror(reccurent_hilbert_to_image(spectrum4).rotate(-90))

        image = four_tile_image(image1, image2, image3, image4)
        image.save('hilbert/{}.png'.format(len(spectrum)))
        return image


def four_tile_image(bottom_left_image, top_left_image, top_right_image, bottom_right_image):
    horisontal_dimension = int(2 * max(
        bottom_left_image.size[0],
        top_left_image.size[0],
        top_right_image.size[0],
        bottom_right_image.size[0])
                               )
    vertical_dimension = int(2 * max(
        bottom_left_image.size[1],
        top_left_image.size[1],
        top_right_image.size[1],
        bottom_right_image.size[1])
                               )
    image = Image.new('L', (horisontal_dimension, vertical_dimension), 'black')
    image.paste(im=bottom_left_image, box=(0, int(vertical_dimension/2)))
    image.paste(im=top_left_image, box=(0, 0))
    image.paste(im=top_right_image, box=(int(horisontal_dimension/2), 0))
    image.paste(im=bottom_right_image, box=(int(horisontal_dimension/2), int(vertical_dimension / 2)))
    return image

def hilbert_image_segment(spectrum):
    image = Image.new('L', (2, 2), "black")
    pixels = image.load()
    # print('pixels: {} spectrum {}'.format(pixels, spectrum))
    pixels[0, 1] = spectrum[0]
    pixels[0, 0] = spectrum[1]
    pixels[1, 0] = spectrum[2]
    pixels[1, 1] = spectrum[3]
    global counter
    image.save('hilbert/imagesegments/segment{}.png'.format(counter))
    counter += 1
    return image

specter = hilbert_spectrum('eggs.png', 5)
print(specter)
hilbert_image(specter, filename='hilberteggs.png')
seq = [floor(255*x/(32**2)) for x in range(32**2)]
hilbert_image(seq,filename='hilbertGrad.png')
# test=[64,128,192,255]
# image = hilbert_image_segment(test)
# image.show()
