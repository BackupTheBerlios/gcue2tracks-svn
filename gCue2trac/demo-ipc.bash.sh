
export MAIN_DIALOG='
			<window>
			  <vbox>
			    <frame DEscription>
			      <text>
			        <label>This is an example window.</label>
			      </text>
			    </frame>
			    <hbox>
						<entry>
						    <default>Default value</default>
						    <variable>ENTRY</variable>
							<input>cue2tracks -c ogg -Q7 -f cp1251 -R "/home/test/Desktop/Андрей Макаревич - У ломбарда/Андрей Макаревич - У ломбарда.cue"</input>
							<action type="refresh">ENTRY</action>
						</entry>
			      <button ok>
						<action>xfce4-terminal -x cue2tracks -c ogg -Q7 -f cp1251 -R "/home/test/Desktop/Андрей Макаревич - У ломбарда/Андрей Макаревич - У ломбарда.cue"</action>
					</button>
			      <button cancel>
					      <label>Launch</label>
					      <action type="launch">BAR_DIALOG</action>
					</button>
			    </hbox>
			  </vbox>
			</window>
  </frame>
  <hbox>
   <button cancel></button>
  </hbox>
'
export BAR_DIALOG='
<vbox>
  <frame Progress>
    <text>
      <label>Some text describing what is happening.</label>
		<input>cue2tracks -c ogg -Q7 -f cp1251 -R "/home/test/Desktop/Андрей Макаревич - У ломбарда/Андрей Макаревич - У ломбарда.cue"</input>
		<action type="refresh">ENTRY</action>
    </text>
    <progressbar>
      <variable>PROGRESS_BAR</variable>
      <label>Some Text</label>
      <input>progress_fast</input>
      <action type="refresh">ENTRY</action>
      <action type="closewindow">BAR_DIALOG</action>
      <action>echo ready</action>
    </progressbar>
  </frame>
  <hbox>
   <button cancel>
     <action type="closewindow">BAR_DIALOG</action>
   </button>
  </hbox>
 </vbox>
'
gtkdialog --program=MAIN_DIALOG
