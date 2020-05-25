import tavish

f = input("Type the name of the file you wish to use.\n>")
id_ = tavish.parse(f, l=False)
print("demos.tf/" + str(id_))

_ = input("Press enter to close this process.")
