import shape_parser

if __name__ == "__main__":
    maker = shape_parser.MapMaker()
    maker.force = False
    maker.make_svg()
    print(maker.routes)