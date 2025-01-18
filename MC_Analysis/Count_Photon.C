//CPP
#include <iostream>
#include <filesystem>
#include <fstream>
#include <algorithm> // 引入 std::sort
//ROOT
#include <TFile.h>
#include <TTree.h>
#include <TVector3.h>
#include <TH1D.h>
#include <TCanvas.h>
//JSAP
#include <JPSimOutput.hh>
//Self-Defined
#include "./Heads/Count_Photon.hh"
#include "./Heads/Base_Functions.hh"


void Count_Photon()
{
    // Paths of Files, Pics and CSV Files
    std::string File_Dir, Pic_Dir, CSV_Dir, CSV_File, concentrator;
    // Loop Data
    const Int_t len = 4;
    Int_t wavelengths[len] = {365, 415, 465, 480};
    Int_t Distance = 1;
    for(int index = 0; index < len; index++ )
    {
        Int_t wavelength = wavelengths[index];
        std::cout << "[Count_Photon] Start Processing " << wavelength << std::endl;
    // PMT
        File_Dir = "/home/penguin/Jinping/JSAP-install/Simulation/Concentrator-Simulation/OutputFiles/Windows/Photon_PMT/L1/Average";
        Pic_Dir = "/home/penguin/Jinping/JSAP-install/Codes/Pics/Windows/L1";
        Pic_Dir = Pic_Dir + "/" + std::to_string(wavelength) + "/" + "PMT";
        CSV_Dir = "/home/penguin/Jinping/JSAP-install/Codes/CSV/MC/Windows";
        CSV_File = CSV_Dir + "/" + "L" + std::to_string(Distance) + "_" + std::to_string(wavelength) + "_PMT.csv";
        concentrator = "0";
        // Count_Photon_All(File_Dir, Pic_Dir, CSV_File, concentrator, wavelength);
    // Concentrator
        File_Dir = "/home/penguin/Jinping/JSAP-install/Simulation/Concentrator-Simulation/OutputFiles/Windows/Photon_Con/L1/Average";
        Pic_Dir = "/home/penguin/Jinping/JSAP-install/Codes/Pics/Windows/L1";
        Pic_Dir = Pic_Dir + "/" + std::to_string(wavelength) + "/" + "Con";
        CSV_Dir = "/home/penguin/Jinping/JSAP-install/Codes/CSV/MC/Windows";
        CSV_File = CSV_Dir + "/" + "L" + std::to_string(Distance) + "_" + std::to_string(wavelength) + "_Con.csv";
        concentrator = "1";
        Count_Photon_All(File_Dir, Pic_Dir, CSV_File, concentrator, wavelength);
        std::cout << "[Count_Photon] Complete!" << std::endl << std::endl;
    };
}
