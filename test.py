def verify_string(input_string):
    if "S01E04" in input_string:
        return True
    else:
        return False

# Test the function
input_string = "Game.of.Thrones.S01E03.Lord.Snow.BR.HDR10.1080p.10Bit.DDP5.1-HEVC-d3g"
if verify_string(input_string):
    print("String contains 'S01E03'")
else:
    print("String does not contain 'S01E03'")
