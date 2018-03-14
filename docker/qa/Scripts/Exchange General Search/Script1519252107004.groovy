import static com.kms.katalon.core.checkpoint.CheckpointFactory.findCheckpoint
import static com.kms.katalon.core.testcase.TestCaseFactory.findTestCase
import static com.kms.katalon.core.testdata.TestDataFactory.findTestData
import static com.kms.katalon.core.testobject.ObjectRepository.findTestObject
import com.kms.katalon.core.checkpoint.Checkpoint as Checkpoint
import com.kms.katalon.core.checkpoint.CheckpointFactory as CheckpointFactory
import com.kms.katalon.core.mobile.keyword.MobileBuiltInKeywords as MobileBuiltInKeywords
import com.kms.katalon.core.mobile.keyword.MobileBuiltInKeywords as Mobile
import com.kms.katalon.core.model.FailureHandling as FailureHandling
import com.kms.katalon.core.testcase.TestCase as TestCase
import com.kms.katalon.core.testcase.TestCaseFactory as TestCaseFactory
import com.kms.katalon.core.testdata.TestData as TestData
import com.kms.katalon.core.testdata.TestDataFactory as TestDataFactory
import com.kms.katalon.core.testobject.ObjectRepository as ObjectRepository
import com.kms.katalon.core.testobject.TestObject as TestObject
import com.kms.katalon.core.webservice.keyword.WSBuiltInKeywords as WSBuiltInKeywords
import com.kms.katalon.core.webservice.keyword.WSBuiltInKeywords as WS
import com.kms.katalon.core.webui.keyword.WebUiBuiltInKeywords as WebUiBuiltInKeywords
import com.kms.katalon.core.webui.keyword.WebUiBuiltInKeywords as WebUI
import internal.GlobalVariable as GlobalVariable
import org.openqa.selenium.Keys as Keys

WebUI.openBrowser('')

WebUI.navigateToUrl('http://nginx/account/login/?next=/')

WebUI.setText(findTestObject('Page_example.com (2)/input_username'), 'admin')

WebUI.setText(findTestObject('Page_example.com (2)/input_password'), 'exchange')

WebUI.click(findTestObject('Page_example.com (2)/button_Log In'))

WebUI.click(findTestObject('Page_Welcome - example.com (2)/span_fa fa-search fa-2x'))

WebUI.click(findTestObject('Page_Search - example.com/i_fa fa-caret-down'))

WebUI.click(findTestObject('Page_Search - example.com/a_Layers'))

WebUI.click(findTestObject('Page_Search - example.com/i_fa fa-caret-down'))

WebUI.click(findTestObject('Page_Search - example.com/a_Documents'))

WebUI.click(findTestObject('Page_Explore Documents - example.co/i_fa fa-caret-down'))

WebUI.click(findTestObject('Page_Explore Documents - example.co/a_Explore Maps'))

WebUI.click(findTestObject('Page_Search - example.com/span_fa fa-search'))

WebUI.click(findTestObject('Page_Search - example.com/a_Exchange'))

WebUI.click(findTestObject('Page_Welcome - example.com (2)/i_fa fa-map fa-4x'))

WebUI.click(findTestObject('Page_Search - example.com/i_fa fa-search'))

WebUI.click(findTestObject('Page_Search - example.com/a_Exchange'))

WebUI.click(findTestObject('Page_Welcome - example.com (2)/i_fa fa-users fa-4x'))

WebUI.click(findTestObject('Page_Search - example.com/i_fa fa-caret-down_1'))

WebUI.click(findTestObject('Page_Welcome - example.com/a_Logout'))

WebUI.closeBrowser()

