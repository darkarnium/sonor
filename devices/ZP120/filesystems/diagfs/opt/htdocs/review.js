function trimAll( strValue ) {
 var objRegExp = /^(\s*)$/;

    //check for all spaces
    if(objRegExp.test(strValue)) {
       strValue = strValue.replace(objRegExp, '');
       if( strValue.length == 0)
          return strValue;
    }

   //check for leading & trailing spaces
   objRegExp = /^(\s*)([\W\w]*)(\b\s*$)/;
   if(objRegExp.test(strValue)) {
       //remove leading and trailing whitespace characters
       strValue = strValue.replace(objRegExp, '$2');
    }
  return strValue;
}

var strengthData = new Array();
var macAddrs = new Array();
var macAddrsToZoneNames = new Array();
	
function finishDrawTable(tbodyID) {
    var th, tr, td, txt, br;
	var zp,nf,ofdm;
    tbody = document.getElementById(tbodyID);
    // create holder for accumulated tbody elements and text nodes
    var frag = document.createDocumentFragment();
    //
    // Make column headings
    //
    tr = document.createElement("tr");
    th = document.createElement("th"); tr.appendChild(th);
    for (var i = 0; i < macAddrs.length; i++) {
	if(macAddrs[i] != "eth0" && macAddrs[i] != "eth1")
	{
        th = document.createElement("th");
	txt = document.createTextNode("Strength to"); th.appendChild(txt);
	br = document.createElement("br"); th.appendChild(br);
        txt = document.createTextNode(macAddrs[i]); th.appendChild(txt);
	br = document.createElement("br"); th.appendChild(br);
        txt = document.createTextNode(macAddrsToZoneNames[macAddrs[i]]); th.appendChild(txt);
	tr.appendChild(th);
	}
    }
    frag.appendChild(tr);
    //
    // loop through data source
    //
    for (var i = 0; i < strengthData.length; i++) {
        var sd = strengthData[i];
    	tr = document.createElement("tr");
    	
    	td = document.createElement("td");
    	td.setAttribute("class", "ctr");

    	txt = document.createTextNode(sd.macAddr); td.appendChild(txt);
        br = document.createElement("br"); td.appendChild(br);

    	txt = document.createTextNode(macAddrsToZoneNames[sd.macAddr]); td.appendChild(txt);
        br = document.createElement("br"); td.appendChild(br);
		
		for(var j = 0; j < sd.destinations.length; j++)
		{
			if(sd.pathCost == 0)
			{
				txt = document.createTextNode("Root Bridge"); td.appendChild(txt);
				break;
			}
			else if(parseInt(sd.pathCost) == (parseInt(sd.destinations[j].pathCost) + parseInt(sd.destinations[j].designatedCost)))
			{
				if(sd.destinations[j].designatedCost == 0)
				{
					txt = document.createTextNode("Secondary Node"); td.appendChild(txt);
				}
				else
				{
					txt = document.createTextNode("Tertiary Node"); td.appendChild(txt);
				}
				break;
			}
		}
		
        br = document.createElement("br"); td.appendChild(br);

        txt = document.createTextNode(sd.noiseFloor); td.appendChild(txt);
        br = document.createElement("br"); td.appendChild(br);

        txt = document.createTextNode(sd.weakSignal); td.appendChild(txt);
		
//added color for ZonePlayer status
		if(sd.noiseFloor && sd.weakSignal)
		{
		if( sd.noiseFloor.match( /Noise Floor: -(\d+), -(\d+), -(\d+)/ ))
			nf = (parseInt(RegExp.$1) + parseInt(RegExp.$2) + parseInt(RegExp.$3))/3;
		else if( sd.noiseFloor.match( /Noise Floor: -(\d+)/ ))
			nf = RegExp.$1;

		if( sd.weakSignal.match( /OFDM Weak signal level: (\d+)/ ))
			ofdm = RegExp.$1;
        else if( sd.weakSignal.match( /OFDM ANI level: (\d+)/ ))
            ofdm = (12 - parseInt(RegExp.$1)) / 2;  // Map 0-9 to 6->1.5
		
		if( nf > 94 && ofdm > 4 )
			td.style.background = "rgb(32,190,32)";
		else if( nf > 89 && ofdm > 3 )
			td.style.background = "rgb(255,255,32)";
		else if( nf > 84 && ofdm > 2 )
			td.style.background = "rgb(255,159,32)";
		else
			td.style.background = "rgb(255,32,32)";
		}	
    	tr.appendChild(td);

        for (var j = 0; j < macAddrs.length; j++) {
			if(macAddrs[j] != "eth0" && macAddrs[j] != "eth1")
			{
       	    td = document.createElement("td");
            for (var k = 0; k < sd.destinations.length; k++) {
                var dst = sd.destinations[k];
                if (dst.addr == macAddrs[j]) {

//added color for Connection status
		    var temp=0,count=0;
		    var dstAvg = new Array();
			dstAvg[0] = dst.inA;
			dstAvg[1] = dst.inB;
			dstAvg[2] = dst.outA;
			dstAvg[3] = dst.outB;

		    for (var l = 0; l < dstAvg.length; l++)
		    {
			if(dstAvg[l])
			{
				temp += parseInt(dstAvg[l]);
				count++;
			}
		    }

		    temp = temp/count;

                    txt = document.createTextNode("Inbound: " + dst.inA + " " + dst.inB);
                    td.appendChild(txt);
                    br = document.createElement("br"); td.appendChild(br);

                    txt = document.createTextNode("Outbound: " + dst.outA + " " + dst.outB);
                    td.appendChild(txt);
                    br = document.createElement("br"); td.appendChild(br);

                    txt = document.createTextNode("STP state: " + dst.stpState);
					if(dst.connects)
					{
						if(temp > 44)
							td.style.background = "rgb(32,190,32)";
						else if(temp > 29)
							td.style.background = "rgb(255,255,32)";
						else if(temp > 17)
							td.style.background = "rgb(255,159,32)";
						else
							td.style.background = "rgb(255,32,32)";
					}
					else
					{
						td.style.background = "rgb(224,224,224)";
					}
					
                    td.appendChild(txt);
		
                    break;
                }
            }
            tr.appendChild(td);
			}
        }

        frag.appendChild(tr);
    }
    if (!tbody.appendChild(frag)) {
    	alert("This browser doesn't support dynamic tables.");
    }
}

function addMacAddr(addr) {
    for (var i = 0; i < macAddrs.length; i++) {
        if (macAddrs[i] == addr) return;
    }
    macAddrs.push(addr);
}

function sortByMACAddr(a, b) {
    var x = a.macAddr;
    var y = b.macAddr;
    return ((x < y) ? -1 : ((x > y) ? 1 : 0));
}

function parseStpData(stpData, nodeDataObj) {

    var lines = stpData.value.split('\n');
    for (var l = 0; l < lines.length; l++) {
        var words = trimAll(lines[l]).split(/\s+/);
        if (words.length > 0) {
            if (words[0] == "ath0" || words[0] == "eth0" || words[0] == "eth1") {
                //
                // This begins a new node section
                //				
				if(words[3] == "tunnel")
				{
					toMAC = words[5];	// MAC address of destination
					rSTP = words[10].replace(/[,\)]/g, '');  // remote STP state
				}
				else
				{
					toMAC = words[0];
					rSTP = words[0];
				}
                //
                // Find an existing destination object, or make a new one if it
                // isn't there yet
                //
                var toNode = null;
                for (var i = 0; i < nodeDataObj.destinations.length; i++) {
                    if (nodeDataObj.destinations[i].addr == toMAC) {
                        toNode = nodeDataObj.destinations[i];
						toNode.remoteState = rSTP;
                        break;
                    }
                }
                if (toNode == null) {
                    toNode = new Object;
                    toNode.addr = toMAC;
					toNode.remoteState = rSTP;
                    nodeDataObj.destinations.push(toNode);
                }
                //
                // Now, parse the rest of the lines in this section. The 
                // section is deliniated by a blank line.
                //
                while (++l < lines.length) {
                    var line = trimAll(lines[l]);
                    if (line.length == 0) break;
                    words = line.split(/\s+/);
                    if (words[0] == "port") {
                        toNode.portID = words[2];
                        toNode.stpState = words[4];
                    } else if (words[1] == "root") {
                        toNode.designatedRoot = words[2];
                        toNode.pathCost = words[5];
                    } else if (words[1] == "bridge") {
                        toNode.designatedBridge = words[2];
                        toNode.msgAgeTimer = words[6];
                    } else if (words[1] == "port") {
                        toNode.designatedPort = words[2];
                        toNode.fwdDelayTimer = words[6];
                    } else if (words[1] == "cost") {
                        toNode.designatedCost = words[2];
                        toNode.holdTimer = words[5];
                    } else if (words[0] == "flags") {
                        toNode.flags = "";
                        for (var i = 1; i < words.length; i++) {
                            if (toNode.flags.length > 0) 
                                toNode.flags = toNode.flags + ",";
                            toNode.flags = toNode.flags + words[i];
                        }
                    }
                }
				if (toNode.remoteState == "forwarding" && toNode.stpState == "forwarding")
					toNode.connects = 1;
				else
					toNode.connects = 0;
				
            } else if (words[0] == "bridge") {
                nodeDataObj.bridgeID = words[2];
            } else if (words[0] == "designated" && words[1] == "root") {
                nodeDataObj.designatedRoot = words[2];
            } else if (words[0] == "root") {
                nodeDataObj.rootPort = words[2];
                nodeDataObj.pathCost = words[5];
            } else if (words[0] == "max") {
                nodeDataObj.maxAge = words[2];
                nodeDataObj.bridgeMaxAge = words[6];
            } else if (words[0] == "hello" && words[1] == "time") {
                nodeDataObj.helloTime = words[2];
                nodeDataObj.bridgeHelloTime = words[6];
            } else if (words[0] == "forward") {
                nodeDataObj.forwardDelay = words[2];
                nodeDataObj.bridgeForwardDelay = words[6];
            } else if (words[0] == "ageing") {
                nodeDataObj.ageingTime = words[2];
                nodeDataObj.gcInterval = words[5];
            } else if (words[0] == "hello" && words[1] == "timer") {
                nodeDataObj.helloTimer = words[2];
                nodeDataObj.tcnTimer = words[5];
            } else if (words[0] == "topology") {
                nodeDataObj.topologyChangeTimer = words[3];
                nodeDataObj.gcTimer = words[6];
            } else if (words[0] == "flags") {
                nodeDataObj.flags = "";
                for (var i = 1; i < words.length; i++) {
                    if (nodeDataObj.flags.length > 0) 
                        nodeDataObj.flags = nodeDataObj.flags + ",";
                    nodeDataObj.flags = nodeDataObj.flags + words[i];
                }
            }
        }
    }
}

function parseIfData(ifData, nodeStrengthData) {
    //
    //	Looking for something like:
    //  ath0      Link encap:Ethernet  HWaddr 00:0E:9B:12:7D:58
    //
    var lines = ifData.value.split('\n');
    for (var l = 0; l < lines.length; l++) {
        var words = trimAll(lines[l]).split(/\s+/);
        if (words[0] == "ath0") {
            nodeStrengthData.macAddr = words[4];
            break;
        } else if (words[0] == "eth0") {
            //
            //	This case is only if we are debugging on the virtual
            //	ZP & Controller which doesn't have ath0.
            //
            if (nodeStrengthData.macAddr == null) 
                nodeStrengthData.macAddr = words[4];
        }
    }
}

function parseNetData(statusData, nodeStrengthData) {
    var noiseFloorNum = 0;
    var lines = statusData.value.split('\n');
	nodeStrengthData.channel = 0;
    for (var l = 0; l < lines.length; l++) {
        var words = trimAll(lines[l]).split(/\s+/);
        if (words.length > 0) {
			if (words[0] == "Operating") {
				nodeStrengthData.channel = (parseInt(words[3])-2407)/5;
            } else if (words[0] == "Noise") {
                if (noiseFloorNum == 0) {
                    nodeStrengthData.noiseFloor = "Noise Floor: " + words[2];
                } else {
                    nodeStrengthData.noiseFloor += ", ";
                    nodeStrengthData.noiseFloor += words[2];
                }
                noiseFloorNum++;
            } else if (words[0] == "OFDM") {
                nodeStrengthData.weakSignal = lines[l];
            } else if (words[0] == "Node") {
                // Node xx:xx:xx:xx:xx:xx - FROM 63 {61} : TO 63 {61} : STP 03
                var sdToNode = new Object();

                // increment wi depending on ':'
                var nextW = 0;
                sdToNode.addr = words[1];
                sdToNode.inA = words[4];
                if (words[5] != ":") {
                    sdToNode.inB = words[5];
                    nextW = 8;
                } else {
                    sdToNode.inB = "";
                    nextW = 7;
                }

                sdToNode.outA = words[nextW];
                if (words[nextW+1] != ":") {
                    sdToNode.outB = words[nextW+1];
                } else {
                    sdToNode.outB = "";
                }

                while (++l < lines.length) {
                    words = trimAll(lines[l]).split(/\s+/);
                    if (words[0] == "Node")
                        break;
                }
                nodeStrengthData.destinations.push(sdToNode);
                l--;
            }
        }
    }
}

function makenetwork() {
    //
    //	If network data is already parsed, bail out now.
    //
    if (strengthData.length > 0) return;
    //
    //	The data for each node is enclosed in a separate DIV. Begin by getting a collection of all
    //	the DIVs which where each DIV will contain the data for a single node.
    //
    var netDataCollection = document.getElementById("netdata").getElementsByTagName("div");
    for (var i = 0; i < netDataCollection.length; i++) {
        var netData = netDataCollection[i];
        //
        //	The name of the DIV will be netdata_RINCON_{UID of node}
        //	
        var dataNameComponents = netData.id.split('_');
        if (dataNameComponents.length == 3) {
            var uid = dataNameComponents[1] + "_" + dataNameComponents[2];
            //
            //	Now, each DIV contains a TEXTAREA with the different data sections we need to parse
            //
            var statusData = document.getElementById("status_" + uid);
            var ifData = document.getElementById("ifconfig_" + uid);
            var stpData = document.getElementById("stp_" + uid);
            var zoneName = document.getElementById("zonename_" + uid).value;

            var nodeStrengthData = new Object();
            //
            //	Find the wireless MAC address for this node from the ifconfig data
            //	If we didn't find it, then just punt this node entirely.
            //
            parseIfData(ifData, nodeStrengthData);
            if (nodeStrengthData.macAddr == null) continue;

            // Store mapping from MAC address to zone name
            macAddrsToZoneNames[nodeStrengthData.macAddr] = zoneName;

            //
            //	Parse the wireless strength data for this node
            //
            nodeStrengthData.destinations = new Array();
            parseNetData(statusData, nodeStrengthData);
            //
            //	Parse the STP data for this node
            //
            parseStpData(stpData, nodeStrengthData);

            strengthData.push(nodeStrengthData);
        }
    }
    //
    // Take a pass thru the parsed data to come up with the complete list
    // of MAC addresses
    //
    for (var i = 0; i < strengthData.length; i++) {
        var sd = strengthData[i];
        addMacAddr(sd.macAddr);
        for (var j = 0; j < sd.destinations.length; j++) {
            var dst = sd.destinations[j];
            addMacAddr(dst.addr);
        }
    }
    finishDrawTable("networkTableBody");
}
