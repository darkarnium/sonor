<?xml version="1.0" encoding="utf-8"?>
<xsl:stylesheet version="1.0" xmlns:xsl="http://www.w3.org/1999/XSL/Transform"><xsl:template match="/">
<html xmlns="http://www.w3.org/1999/xhtml">
    <head></head>
    <body>
        Challenge: <xsl:value-of select="/factoryResetKeys/challenge" /><br />
        
        <form action="/reboot" method="POST">
            <input type="hidden" name="reset" value="yes"/>
            <label for="confirm">Confirmation Token: </label><input type="text" name="confirm" id="confirm" /><br />
            <button type="submit">Confirm</button>
        </form>
    </body>
</html>
</xsl:template></xsl:stylesheet>
