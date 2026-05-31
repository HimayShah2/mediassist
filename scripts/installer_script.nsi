; MediAssist Pro NSIS Installer Script
; --------------------------------------

!define APP_NAME "MediAssist Pro"
!define COMP_NAME "MediAssist"
!define VERSION "2.0.0"
!define EXE_NAME "MediAssistPro.exe"

; Main Install Settings
Name "${APP_NAME}"
OutFile "..\dist\MediAssistPro_Setup_v${VERSION}.exe"
InstallDir "$PROGRAMFILES64\${APP_NAME}"
RequestExecutionLevel admin

; Include modern UI
!include "MUI2.nsh"

; Interface Settings
!define MUI_ABORTWARNING
; !define MUI_ICON "assets\icons\app.ico" ; Ensure you have an icon at this path

; Pages
!insertmacro MUI_PAGE_WELCOME
!insertmacro MUI_PAGE_DIRECTORY
!insertmacro MUI_PAGE_INSTFILES
!insertmacro MUI_PAGE_FINISH

!insertmacro MUI_UNPAGE_CONFIRM
!insertmacro MUI_UNPAGE_INSTFILES

; Languages
!insertmacro MUI_LANGUAGE "English"

; --------------------------------------
; Install Section
; --------------------------------------
Section "Main Section" SEC01
    SetOutPath "$INSTDIR"
    
    ; Copy all files from the PyInstaller --onedir output
    File /r "..\dist\MediAssistPro\*.*"
    
    ; Create Uninstaller
    WriteUninstaller "$INSTDIR\Uninstall.exe"
    
    ; Create Shortcuts
    CreateShortCut "$DESKTOP\${APP_NAME}.lnk" "$INSTDIR\${EXE_NAME}"
    CreateDirectory "$SMPROGRAMS\${APP_NAME}"
    CreateShortCut "$SMPROGRAMS\${APP_NAME}\${APP_NAME}.lnk" "$INSTDIR\${EXE_NAME}"
    CreateShortCut "$SMPROGRAMS\${APP_NAME}\Uninstall.lnk" "$INSTDIR\Uninstall.exe"
    
    ; Add to Add/Remove Programs
    WriteRegStr HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\${APP_NAME}" "DisplayName" "${APP_NAME}"
    WriteRegStr HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\${APP_NAME}" "UninstallString" "$INSTDIR\Uninstall.exe"
    WriteRegStr HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\${APP_NAME}" "DisplayIcon" "$INSTDIR\${EXE_NAME}"
    WriteRegStr HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\${APP_NAME}" "DisplayVersion" "${VERSION}"
SectionEnd

; --------------------------------------
; Uninstaller Section
; --------------------------------------
Section "Uninstall"
    Delete "$DESKTOP\${APP_NAME}.lnk"
    RMDir /r "$SMPROGRAMS\${APP_NAME}"
    RMDir /r "$INSTDIR"
    DeleteRegKey HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\${APP_NAME}"
SectionEnd
