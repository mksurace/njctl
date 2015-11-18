from org.sikuli.script.natives import Vision
# Vision.setParameter("MinTargetSize", 6)


waitVanish("1447860363687.png")


waitVanish("1447860673146.png")
wait("1447860708512.png", FOREVER)

click("1447860457604.png")
type("f", Key.ALT)
type("e")
type("d")
# Click Full Page
wait("1447860815830.png", FOREVER)
click("1447860822195.png")
# Delete the Header/Date fields
type(Key.TAB)
type("x", Key.CTRL)
type(Key.TAB)
type(Key.TAB)
type(Key.DELETE)
# Set to Landscape
click("1447771403950.png")
wait("1447860873420.png", FOREVER)

click("1447771417897.png")
# Save the PDF
type(Key.ENTER)
wait("1447861698414.png", FOREVER)
wait("1447861716988.png", FOREVER)
sleep(2)
# Enter Filename
type("v", Key.CTRL)
# Delete notebook from the end.
type(Key.BACKSPACE)
type(Key.BACKSPACE)
type(Key.BACKSPACE)
type(Key.BACKSPACE)
type(Key.BACKSPACE)
type(Key.BACKSPACE)
type(Key.BACKSPACE)
type(Key.BACKSPACE)
type(Key.BACKSPACE)
type(Key.HOME)
type("D:\\PDFs\\")
# Save!
type(Key.ENTER)
waitVanish("1447862138132.png")
