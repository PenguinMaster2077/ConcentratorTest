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


void Count_Photon(Int_t Distance, std::string Path)
{
    // Paths of Files, Pics and CSV Files
    std::string File_Dir, Pic_Dir, CSV_Dir, CSV_File, concentrator;
    // Loop Data
    const Int_t len = 4;
    Int_t wavelengths[len] = {365, 415, 465, 480};
    for(int index = 0; index < len; index++ )
    {
        Int_t wavelength = wavelengths[index];
        std::cout << "[Count_Photon] Start Processing " << wavelength << std::endl;
    // PMT
        std::string Number = Path;
        File_Dir = "/mnt/e/PMT/" + Number + "/PMT";
        if (wavelength == 365)
        {
            Pic_Dir = "/mnt/e/PMT/" + Number + "/Pics/PMT";
        }
        else
        {
            Pic_Dir = "0";
        }
        CSV_Dir = "/mnt/e/PMT/" + Number + "/CSV";
        CSV_File = CSV_Dir + "/" + "L" + std::to_string(Distance) + "_" + std::to_string(wavelength) + "_PMT.csv";
        concentrator = "0";
        Count_Photon_All(File_Dir, Pic_Dir, CSV_File, concentrator, wavelength, Distance);
    // Concentrator
        File_Dir = "/mnt/e/PMT/" + Number + "/Concentrator";
        if (wavelength == 365)
        {
            Pic_Dir = "/mnt/e/PMT/" + Number + "/Pics/Concentrator";
        }
        else
        {
            Pic_Dir = "0";
        }
        CSV_Dir = "/mnt/e/PMT/" + Number + "/CSV";
        CSV_File = CSV_Dir + "/" + "L" + std::to_string(Distance) + "_" + std::to_string(wavelength) + "_Con.csv";
        concentrator = "1";
        Count_Photon_All(File_Dir, Pic_Dir, CSV_File, concentrator, wavelength, Distance);
        std::cout << "[Count_Photon] Complete!" << std::endl << std::endl;
    };
}
